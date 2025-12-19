import json
import logging
import re
from typing import Any, List, Dict, Optional
from pydantic import ValidationError
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from app.services.chat.agent.schema import AgentState, ProductDisplay, MessageModel

# Import shared resources and prompts
from app.services.chat.agent import shared
from app.services.chat.agent.prompts import (
    reasoner_prompt, clarification_prompt, classification_prompt,
    policy_prompt, policy_synthesis_prompt,
    answer_prompt, error_response_prompt, general_responder_prompt
)

# Helper to get resources with lazy initialization
def _get_llm():
    return shared.get_llm_client()

def _get_tools():
    return shared.get_tools()

def _get_tools_list():
    return shared.get_tools_list()

def _get_schema_manager():
    return shared.get_schema_manager()

logger = logging.getLogger(__name__)

def _convert_history_to_langchain_messages(history: List[MessageModel]) -> List[BaseMessage]:
    """Converts a list of MessageModel into a list of LangChain BaseMessage objects."""
    messages = []
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
    return messages


async def classify_intent(state: AgentState) -> dict:
    """Classify the user's intent and update current/last intent state."""
    logger.info(f"[CLASSIFY_INTENT] Input: {state.input}")
    
    history = state.conversation_history or []
    logger.info(f"[CLASSIFY_INTENT] History length: {len(history)}")
    
    history_text = ""
    try:
        history_items = []
        for m in history[-6:]:
            if hasattr(m, 'role') and hasattr(m, 'content'):
                role = m.role
                content = m.content
            elif hasattr(m, 'type') and hasattr(m, 'content'):
                role = m.type
                content = m.content
            elif isinstance(m, dict):
                role = m.get('role', m.get('type', 'unknown'))
                content = m.get('content', str(m))
            else:
                logger.warning(f"[CLASSIFY_INTENT] Unknown message format: {type(m)}, {m}")
                role = 'unknown'
                content = str(m)
            
            history_items.append(f"{role}: {content}")
        history_text = "\n".join(history_items) if history_items else "No previous conversation"
        logger.info(f"[CLASSIFY_INTENT] History text: {history_text}")
    except Exception as e:
        logger.error(f"[CLASSIFY_INTENT] Error building history text: {e}")
        history_text = "No previous conversation"
    
    try:
        logger.debug(f"[CLASSIFY_INTENT] Formatting messages with input='{state.input}' and history='{history_text}'")
        messages = classification_prompt.format_messages(
            input=state.input,
            history=history_text
        )
        logger.debug(f"[CLASSIFY_INTENT] Messages formatted successfully: {messages}")
    except Exception as e:
        logger.error(f"[CLASSIFY_INTENT] Error formatting messages: {e}")
        raise
    
    try:
        response = await _get_llm().ainvoke(
            messages,
            generation_config={"response_mime_type": "application/json"}
        )
        logger.debug(f"[CLASSIFY_INTENT] Raw response type: {type(response)}")
        logger.debug(f"[CLASSIFY_INTENT] Raw response: {response}")
        
        content = response.content if isinstance(response, AIMessage) else str(response)
        logger.debug(f"[CLASSIFY_INTENT] Extracted content: {content}")
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        content = content.strip()
        logger.debug(f"[CLASSIFY_INTENT] Cleaned content: {content}")
        
        result = json.loads(content)
        logger.debug(f"[CLASSIFY_INTENT] Parsed JSON result: {result}")
        new_intent = result.get("intent", "general")
        
        valid_intents = ["product_search", "product_support", "cart_addition", "policy", "unclear", "general", "unsupported"]
        if new_intent not in valid_intents:
            logger.warning(f"[CLASSIFY_INTENT] Invalid intent '{new_intent}', defaulting to 'general'")
            new_intent = "general"
        
        logger.info(f"[CLASSIFY_INTENT] Detected intent: {new_intent}")
        
        last_intent = state.last_intent
        if new_intent not in ("general", "unclear", "unsupported"):
            last_intent = new_intent
            
        return {
            "current_intent": new_intent,
            "last_intent": last_intent
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"[CLASSIFY_INTENT] JSON parse error: {e}")
        logger.error(f"[CLASSIFY_INTENT] Problematic content: {content}")
        return {
            "current_intent": "general",
            "last_intent": state.last_intent
        }
    except KeyError as e:
        logger.error(f"[CLASSIFY_INTENT] Missing key in JSON: {e}")
        return {
            "current_intent": "general",
            "last_intent": state.last_intent
        }
    except Exception as e:
        logger.error(f"[CLASSIFY_INTENT] Unexpected error: {e}", exc_info=True)
        return {
            "current_intent": "general",
            "last_intent": state.last_intent
        }


async def unsupported_responder(state: AgentState) -> dict:
    """(Unsupported Flow) Politely declines requests the agent cannot fulfill."""
    logger.info(f"[UNSUPPORTED_RESPONDER] Input: {state.input}")
    output = ("I'm sorry, I can't "
              "help with that particular request. I can help with finding "
              "products, checking policies, or managing your cart.")
    return {"output": output}


async def policy_reasoner(state: AgentState) -> dict:
    """(Policy Flow) Generate tool calls to answer policy questions."""
    logger.info(f"[POLICY_REASONER] Input: {state.input}")
    
    messages = policy_prompt.format_messages(input=state.input)
    
    response = await _get_llm().bind_tools(_get_tools_list().ainvoke(messages))
    logger.info(f"[POLICY_REASONER] Raw LLM response: {response!r}")

    normalized = []
    has_tool_calls = False
    if isinstance(response, AIMessage) and response.tool_calls:
        has_tool_calls = True
        for call in response.tool_calls:
            normalized.append({
                "name": call.get("name"),
                "args": call.get("args", {})
            })
    else:
        normalized = [{"text": response.content if isinstance(response, AIMessage) else str(response)}]

    logger.info(f"[POLICY_REASONER] Normalized tool calls: {normalized}")
    return {
        "tool_results": normalized,
        "has_tool_calls": has_tool_calls
    }


async def general_responder(state: AgentState) -> dict:
    """(General Flow) Responds to general queries with tool access."""
    logger.info(f"[GENERAL_RESPONDER] Input: {state.input}")
    
    # Get conversation history
    langchain_history = _convert_history_to_langchain_messages(state.conversation_history[-4:])
    
    # Format messages with tools available
    messages = general_responder_prompt.format_messages(
        input=state.input,
        history=langchain_history
    )
    
    # Try to use tools if model supports them, otherwise fallback to no tools
    try:
        llm_with_tools = _get_llm().bind_tools(_get_tools_list())
        response = await llm_with_tools.ainvoke(messages)
    except Exception as e:
        logger.warning(f"[GENERAL_RESPONDER] Tool binding failed ({e}), falling back to no tools")
        response = await _get_llm().ainvoke(messages)
    logger.info(f"[GENERAL_RESPONDER] Raw LLM response: {response!r}")
    
    # Check if LLM made tool calls
    normalized = []
    has_tool_calls = False
    
    if isinstance(response, AIMessage) and response.tool_calls:
        has_tool_calls = True
        logger.info(f"[GENERAL_RESPONDER] Tool calls detected: {len(response.tool_calls)}")
        for call in response.tool_calls:
            normalized.append({
                "name": call.get("name"),
                "args": call.get("args", {})
            })
    else:
        # No tool calls, just return the text response
        output = response.content if isinstance(response, AIMessage) else str(response)
        logger.info(f"[GENERAL_RESPONDER] Direct response (no tools): {output}")
        return {"output": output}
    
    logger.info(f"[GENERAL_RESPONDER] Normalized tool calls: {normalized}")
    return {
        "tool_results": normalized,
        "has_tool_calls": has_tool_calls
    }


async def shopping_reasoner(state: AgentState) -> dict:
    """(Product Search Flow) Generate tool calls to search for products."""
    logger.info(f"[LLM_REASONER] Input: {state.input}")
    
    search_tools_list = [t for t in _get_tools_list() if t.name != "add_to_cart"]
    schema_string = await _get_schema_manager().get_dynamic_schema_string(
        tool_names=["text_search", "hybrid_search", "get_product_by_id", "get_products_by_filter", "weaviate_hybrid_text_search", "weaviate_semantic_text_search", "mongo_find_by_filter"]
    )
    
    langchain_history = _convert_history_to_langchain_messages(state.conversation_history[-4:])
    
    messages = reasoner_prompt.format_messages(
        input=state.input,
        extracted_filters=json.dumps(state.extracted_filters or {}),
        available_schema=schema_string,
        user_id=state.user_id,
        history=langchain_history
    )
    
    response = await _get_llm().bind_tools(search_tools_list).ainvoke(messages)
    logger.info(f"[LLM_REASONER] Raw LLM response: {response!r}")

    normalized = []
    has_tool_calls = False
    if isinstance(response, AIMessage):
        if response.tool_calls:
            has_tool_calls = True
            for call in response.tool_calls:
                normalized.append({
                    "name": call.get("name"),
                    "args": call.get("args", {})
                })
        else:
            text_content = ""
            if isinstance(response.content, str):
                text_content = response.content
            elif isinstance(response.content, list):
                for block in response.content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text_content += block.get('text', '')
                    elif isinstance(block, str):
                        text_content += block
            normalized = [{"text": text_content}]
    elif isinstance(response, str):
        try:
            parsed = json.loads(response)
            normalized = parsed if isinstance(parsed, list) else [parsed]
            has_tool_calls = any("name" in item for item in normalized if isinstance(item, dict))
        except Exception:
            normalized = [{"text": response}]
    else:
        normalized = [{"text": str(response)}]

    logger.info(f"[LLM_REASONER] Normalized tool calls: {normalized}, has_tool_calls: {has_tool_calls}")
    return {
        "tool_results": normalized,
        "has_tool_calls": has_tool_calls
    }


async def cart_reasoner(state: AgentState) -> dict:
    """(Cart Addition Flow) Manages multi-step cart addition."""
    logger.info(f"[CART_REASONER] Input: {state.input}")
    
    cart_tool_names = ["add_to_cart", "get_product_by_id", "text_search", "weaviate_semantic_text_search"]
    cart_tools_list = [t for t in _get_tools_list() if t.name in cart_tool_names]
    schema_string = await _get_schema_manager().get_dynamic_schema_string(tool_names=cart_tool_names)

    pending_action = state.pending_cart_action or {}
    
    if not pending_action.get("item_id") and state.focused_product_id:
        logger.info(f"[CART_REASONER] Using focused_product_id: {state.focused_product_id}")
        pending_action["item_id"] = state.focused_product_id
    
    if pending_action.get("item_id") and not pending_action.get("item_name"):
        try:
            logger.info(f"[CART_REASONER] Pre-fetching product details for {pending_action['item_id']}")
            product = await _get_tools()["get_product_by_id"].ainvoke({"item_id": pending_action["item_id"]})
            if product and not product.get("error"):
                pending_action["item_name"] = product.get("name", "the item")
                pending_action["available_variety"] = product.get("variety", [])
                pending_action["available_color"] = product.get("color", [])
        except Exception as e:
            logger.error(f"[CART_REASONER] Failed to pre-fetch product details: {e}")

    if pending_action.get("item_id"):
        logger.info(f"[CART_REASONER] Extracting details from input: '{state.input}'")
        extracted = extract_variety_color(
            state.input,
            pending_action.get("available_variety", []),
            pending_action.get("available_color", [])
        )
        if extracted.get("variety") and not pending_action.get("variety"):
            pending_action["variety"] = extracted["variety"]
            logger.info(f"[CART_REASONER] Extracted variety: {extracted['variety']}")
        if extracted.get("color") and not pending_action.get("color"):
            pending_action["color"] = extracted["color"]
            logger.info(f"[CART_REASONER] Extracted color: {extracted['color']}")
        
    if (
        pending_action.get("item_id")
        and pending_action.get("variety")
        and pending_action.get("color")
    ):
        logger.info("[CART_REASONER] ✅ All details present. Adding to cart WITHOUT LLM.")
        logger.info(f"[CART_REASONER] Cart details: item_id={pending_action['item_id']}, "
                   f"variety={pending_action['variety']}, color={pending_action['color']}")
        
        result = await _get_tools()["add_to_cart"].ainvoke({
            "user_id": state.user_id,
            "item_id": pending_action["item_id"],
            "variety": pending_action["variety"],
            "color": pending_action["color"],
            "quantity": 1
        })
        logger.info(f"[CART_REASONER] Direct add_to_cart result: {result}")
        return {
            "tool_results": [result],
            "has_tool_calls": False,
            "cart_action_result": result,
            "pending_cart_action": None
        }

    logger.info("[CART_REASONER] Missing details. Calling LLM for next step.")
    
    langchain_history = _convert_history_to_langchain_messages(state.conversation_history[-4:])

    prompt_kwargs = {
        "input": state.input,
        "pending_cart_action": json.dumps(pending_action),
        "available_schema": schema_string,
        "user_id": state.user_id,
        "history": langchain_history,
        "item_name": pending_action.get("item_name", "the item"),
        "available_variety": pending_action.get("available_variety", []),
        "available_color": pending_action.get("available_color", [])
    }
    
    messages = cart_prompt.format_messages(**prompt_kwargs)
    
    response = await _get_llm().bind_tools(cart_tools_list).ainvoke(messages)
    logger.info(f"[CART_REASONER] Raw LLM response: {response!r}")
    
    normalized = []
    has_tool_calls = False
    
    text_response = None
    if isinstance(response, AIMessage) and not response.tool_calls:
        if isinstance(response.content, str):
            text_response = response.content
        elif isinstance(response.content, list):
            text_response = "".join(
                b.get("text", "") for b in response.content if isinstance(b, dict) and b.get("type") == "text"
            )
        normalized = [{"text": text_response}]
        
    elif isinstance(response, AIMessage) and response.tool_calls:
        has_tool_calls = True
        for call in response.tool_calls:
            normalized.append({
                "name": call.get("name"),
                "args": call.get("args", {})
            })
            
            if call.get("name") == "add_to_cart":
                logger.info("[CART_REASONER] LLM called add_to_cart")
            elif call.get("name") in ("get_product_by_id", "text_search", "weaviate_semantic_text_search"):
                logger.info("[CART_REASONER] LLM is searching for product")
                
    elif isinstance(response, str):
        normalized = [{"text": response}]
    else:
        normalized = [{"text": str(response)}]

    return {
        "tool_results": normalized,
        "has_tool_calls": has_tool_calls,
        "pending_cart_action": pending_action or None
    }

async def tool_executor(state: AgentState) -> dict:
    """Execute tool calls with LLM fallback for errors."""
    logger.info(f"[TOOL_EXECUTOR] Tool calls received: {state.tool_results}")

    if not state.tool_results:
        logger.info("[TOOL_EXECUTOR] No tool calls to execute.")
        return {"tool_results": []}

    executed_results = []
    products = []
    cart_action_result = None
    error_context = []
    
    pending_cart_action = state.pending_cart_action
    focused_product_id = state.focused_product_id
    
    for call in state.tool_results:
        tool_name = call.get("name")
        args = call.get("args", {})

        if not tool_name:
            logger.info(f"[TOOL_EXECUTOR] Skipping non-tool item: {call}")
            executed_results.append(call)
            continue

        logger.info(f"[TOOL_EXECUTOR] Executing tool: {tool_name} with args: {args}")

        if tool_name in tools:
            try:
                result = await _get_tools()[tool_name].ainvoke(args)
                logger.info(f"[TOOL_EXECUTOR] Result: {result}")
                
                if tool_name == "add_to_cart":
                    cart_action_result = result
                    executed_results.append(result)
                    pending_cart_action = None
                
                elif tool_name in ("get_product_by_id", "weaviate_semantic_text_search") and state.current_intent == "product_support":
                    if isinstance(result, dict) and "name" in result:
                        product = result
                    elif isinstance(result, list) and len(result) > 0:
                        product = result[0]
                    else:
                        product = None
                    
                    if product:
                        focused_product_id = str(product.get('_id') or product.get('id') or product.get('mongoId'))
                        logger.info(f"[TOOL_EXECUTOR] Set focused_product_id: {focused_product_id}")
                        executed_results.append(product)
                    else:
                        logger.warning("[TOOL_EXECUTOR] Product support search returned no valid product")
                        error_context.append({
                            "tool": tool_name,
                            "user_query": state.input,
                            "error": "No product found matching the search criteria"
                        })

                elif tool_name in ("get_product_by_id", "text_search", "weaviate_semantic_text_search", "weaviate_hybrid_text_search") and state.current_intent == "cart_addition":
                    if isinstance(result, list) and len(result) > 0:
                        product = result[0]
                    elif isinstance(result, dict) and "name" in result:
                        product = result
                    else:
                        product = None

                    if product:
                        logger.info(f"[TOOL_EXECUTOR] Found product for cart: {product.get('name')}")
                        pending_cart_action = {
                            "item_id": str(product.get('_id') or product.get('id') or product.get('mongoId')),
                            "item_name": product.get("name", "the item"),
                            "available_variety": product.get("variety", []),
                            "available_color": product.get("color", []),
                            "variety": None,
                            "color": None
                        }
                        logger.info(f"[TOOL_EXECUTOR] Set pending_cart_action: {pending_cart_action}")
                    else:
                        error_context.append({
                            "tool": tool_name,
                            "user_query": state.input,
                            "error": "Could not find the product you're looking for"
                        })
                    
                    executed_results.append({"text": f"Found product: {product.get('name') if product else 'not found'}"})

                elif isinstance(result, list) and len(result) > 0 and "name" in result[0]:
                    formatted_products = []
                    for item in result:
                        try:
                            item['id'] = str(item.get('_id', ''))
                            if 'stock' not in item:
                                item['in_stock'] = True
                            else:
                                item['in_stock'] = item.get('stock', 0) > 0
                            
                            validated_product = ProductDisplay(**item)
                            formatted_products.append(validated_product.model_dump())
                        except ValidationError as e:
                            logger.warning(f"[TOOL_EXECUTOR] Failed to validate product: {item.get('name')}. Error: {e}")
                    
                    if not formatted_products:
                        error_context.append({
                            "tool": tool_name,
                            "user_query": state.input,
                            "error": "Found items but couldn't validate them properly"
                        })
                    else:
                        products.extend(formatted_products)
                        executed_results.extend(formatted_products)
                else:
                    executed_results.extend(result if isinstance(result, list) else [result])
                    
            except Exception as e:
                logger.error(f"[TOOL_EXECUTOR] Tool {tool_name} failed: {e}", exc_info=True)
                error_context.append({
                    "tool": tool_name,
                    "user_query": state.input,
                    "error": str(e),
                    "args": args
                })
        else:
            logger.warning(f"[TOOL_EXECUTOR] Unknown tool: {tool_name}")
            error_context.append({
                "tool": tool_name,
                "user_query": state.input,
                "error": f"Tool '{tool_name}' does not exist"
            })

    logger.info(f"[TOOL_EXECUTOR] Executed results: {executed_results}")
    
    return {
        "tool_results": executed_results,
        "products": products if products else None,
        "cart_action_result": cart_action_result,
        "pending_cart_action": pending_cart_action,
        "focused_product_id": focused_product_id,
        "execution_errors": error_context if error_context else None 
    }
    
async def format_results(state: AgentState) -> dict:
    """Format the final output with LLM-powered error handling."""
    logger.info(f"[FORMATTER] Processing state (Current Intent: {state.current_intent}, Last: {state.last_intent})")

    if state.execution_errors:
        logger.info(f"[FORMATTER] Handling execution errors: {state.execution_errors}")
        
        error_details = "\n".join([
            f"- Attempted to use tool '{err['tool']}' but {err['error']}"
            for err in state.execution_errors
        ])
        
        messages = error_response_prompt.format_messages(
            error_details=error_details,
            user_query=state.input
        )
        
        response = await _get_llm().ainvoke(messages)
        output = response.content if isinstance(response, AIMessage) else str(response)
        
        logger.info(f"[FORMATTER] LLM-generated error response: {output}")
        return {"output": output}

    if state.output:
        logger.info(f"[FORMATTER] Returning direct output: {state.output}")
        return {"output": state.output}

    if state.cart_action_result:
        cart_result = state.cart_action_result
        if cart_result.get("success"):
            if cart_result.get('action') == 'added':
                output = (
                    f"✅ **{cart_result.get('item_name')}** has been added to your cart.\n"
                    f"(Price: ${cart_result.get('price')}, Quantity: {cart_result.get('quantity')})"
                )
            else:
                output = f"✅ Quantity for **{cart_result.get('item_name')}** updated to {cart_result.get('quantity')}."
        else:
            output = f"❌ {cart_result.get('message')}"
        
        logger.info(f"[FORMATTER] Cart action output: {output}")
        return {"output": output}
    
    if (
        state.current_intent == "cart_addition"
        and state.pending_cart_action
        and state.pending_cart_action.get("item_id")
    ):
        pending = state.pending_cart_action
        
        logger.info("[FORMATTER] Returning variant selector UI data")
        return {
            "output": f"Great! I found **{pending.get('item_name', 'the item')}**. Please select your preferences:",
            "show_variant_selector": True,
            "variant_data": {
                "item_id": pending.get("item_id"),
                "item_name": pending.get("item_name"),
                "available_variety": pending.get("available_variety", []),
                "available_color": pending.get("available_color", [])
            }
        }
    
    if not state.tool_results:
        logger.info("[FORMATTER] No tool results found.")
        messages = error_response_prompt.format_messages(
            error_details="No results were returned from the search",
            user_query=state.input
        )
        response = await _get_llm().ainvoke(messages)
        output = response.content if isinstance(response, AIMessage) else str(response)
        return {"output": output}

    results: List[Dict[str, Any]] = state.tool_results

    if state.products and len(state.products) > 0:
        output = f"I found {len(state.products)} item(s) for you! 🛍️\n\n"
        output += "Check out the products below. Click on any item to view details, or let me know if you'd like to add any to your cart!"
        logger.info("[FORMATTER] Returning visual product list.")
        return {"output": output}

    if state.last_intent == "policy":
        logger.info("[FORMATTER] Synthesizing policy answer...")
        
        policy_texts = [
            r.get('policy') for r in results if isinstance(r, dict) and r.get('policy')
        ]
        
        if not policy_texts:
            logger.info("[FORMATTER] Policy intent but no policy text found.")
            messages = error_response_prompt.format_messages(
                error_details="No matching policy documents were found",
                user_query=state.input
            )
            response = await _get_llm().ainvoke(messages)
            output = response.content if isinstance(response, AIMessage) else str(response)
            return {"output": output}

        policy_context = "\n\n---\n\n".join(policy_texts)
        
        messages = policy_synthesis_prompt.format_messages(
            policy_context=policy_context,
            input=state.input
        )
        
        response = await _get_llm().ainvoke(messages)
        output = response.content if isinstance(response, AIMessage) else str(response)
        
        logger.info(f"[FORMATTER] Returning synthesized policy response: {output}")
        return {"output": output}

    formatted_items = []
    for r in results[:5]:
        if "name" in r or "price" in r:
            item_text = f"- **{r.get('name', 'Unknown Item')}**"
            if "price" in r:
                item_text += f" - ${r.get('price')}"
            if "brand" in r:
                item_text += f" ({r.get('brand')})"
            formatted_items.append(item_text)
    
    if formatted_items:
        output = f"I found {len(results)} item(s) for you:\n\n" + "\n".join(formatted_items)
        if len(results) > 5:
            output += f"\n\n...and {len(results) - 5} more items."
        output += "\n\nWould you like to add any items to your cart?"
        logger.info("[FORMATTER] Returning formatted text-product list.")
        return {"output": output}

    if len(results) == 1 and "text" in results[0] and "name" not in results[0]:
        text_content = results[0]["text"]
        if isinstance(text_content, str):
            output = text_content
        elif isinstance(text_content, list):
            output = "".join(b.get("text", "") for b in text_content if isinstance(b, dict) and b.get("type") == "text")
        else:
            output = str(text_content)
            
        logger.info(f"[FORMATTER] Returning single text response: {output}")
        return {"output": output}

    logger.info("[FORMATTER] Tool results found but no formatting rule matched.")
    messages = error_response_prompt.format_messages(
        error_details="Search completed but no matching products were found with the specified criteria",
        user_query=state.input
    )
    response = await _get_llm().ainvoke(messages)
    output = response.content if isinstance(response, AIMessage) else str(response)
    return {"output": output}

def is_confirmation(text: str) -> bool:
    """Check if user is confirming an action."""
    affirmatives = ["yes", "yeah", "yep", "yup", "sure", "ok", "okay", "correct", "right", "confirm", "exactly", "that's right"]
    negatives = ["no", "nope", "nah", "cancel", "nevermind", "changed my mind"]
    lower_text = text.lower().strip()
    if any(neg in lower_text for neg in negatives):
        return False
    return any(aff in lower_text for aff in affirmatives)


def extract_variety_color(text: str, available_variety: list, available_color: list) -> Dict[str, Optional[str]]:
    """
    Extract variety and color mentions from user input with exact matching.
    Returns the first exact match found for each.
    """
    result = {"variety": None, "color": None}
    lower_text = text.lower()
    
    for v in available_variety:
        pattern = r'\b' + re.escape(v.lower()) + r'\b'
        if re.search(pattern, lower_text):
            result["variety"] = v
            logger.info(f"[EXTRACT] Found variety '{v}' in '{text}'")
            break
    
    for c in available_color:
        if c.lower() in lower_text:
            result["color"] = c
            logger.info(f"[EXTRACT] Found color '{c}' in '{text}'")
            break
    
    return result


async def analyze_query(state: AgentState) -> dict:
    """
    (Product Search Flow) Prepares the state for the shopping_reasoner.
    """
    logger.info(f"[ANALYZE_QUERY] (Search Flow) Entering search branch.")
    
    return {
        "pending_cart_action": None,
        "extracted_filters": state.extracted_filters or {},
        "products": None
    }
    
async def product_support_reasoner(state: AgentState) -> dict:
    """
    Handles product support queries in a single self-contained flow.
    1. If no focused_product_id → search for the product (tool call).
    2. If focused_product_id exists but product data not fetched → fetch it directly.
    3. If product data exists → answer user's question using it.
    """

    logger.info(f"[PRODUCT_SUPPORT_REASONER] Input: {state.input}")
    logger.info(f"[PRODUCT_SUPPORT_REASONER] Focused Product ID: {state.focused_product_id}")

    if not state.focused_product_id:
        logger.info("[PRODUCT_SUPPORT_REASONER] No focused product → searching.")
        search_tools_list = [t for t in _get_tools_list() if t.name in ["weaviate_semantic_text_search", "get_product_by_id"]]
        messages = product_support_search_prompt.format_messages(input=state.input)
        response = await _get_llm().bind_tools(search_tools_list).ainvoke(messages)

        normalized = []
        if isinstance(response, AIMessage) and response.tool_calls:
            for call in response.tool_calls:
                normalized.append({"name": call.get("name"), "args": call.get("args", {})})

        return {"tool_results": normalized, "has_tool_calls": bool(normalized)}

    logger.info(f"[PRODUCT_SUPPORT_REASONER] Focused product exists → ID {state.focused_product_id}")

    product_data = None
    if state.tool_results:
        for result in state.tool_results:
            if isinstance(result, dict) and str(result.get("_id") or result.get("mongoId")) == state.focused_product_id:
                product_data = result
                logger.info("[PRODUCT_SUPPORT_REASONER] Found product data in state.tool_results.")
                break

    if not product_data:
        logger.info("[PRODUCT_SUPPORT_REASONER] Fetching product details...")
        product = await _get_tools()["get_product_by_id"].ainvoke({"item_id": state.focused_product_id})
        if not product or "error" in product:
            return {"output": "Sorry, I couldn’t find details for that product."}
        product_data = product

    logger.info("[PRODUCT_SUPPORT_REASONER] Generating answer from product data.")
    messages = answer_prompt.format_messages(
        product_name=product_data.get("name", "Unknown"),
        product_description=product_data.get("description", "No description available"),
        product_price=product_data.get("price", 0),
        product_brand=product_data.get("brand", "Unknown"),
        product_variety=", ".join(product_data.get("variety", [])),
        product_colors=", ".join(product_data.get("color", [])),
        product_stock=product_data.get("stock", 0),
        input=state.input
    )

    response = await _get_llm().ainvoke(messages)
    answer = response.content if isinstance(response, AIMessage) else str(response)

    logger.info(f"[PRODUCT_SUPPORT_REASONER] Final answer: {answer}")
    return {"output": answer, "has_tool_calls": False, "tool_results": [{"text": answer}]}

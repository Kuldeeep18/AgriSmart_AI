import os
import random
from flask import Blueprint, request, jsonify

chatbot_bp = Blueprint("chatbot", __name__, template_folder="templates", static_folder="static")

OFFLINE_KNOWLEDGE = {
    "wheat": "Wheat thrives in well-drained loamy soil with temperatures between 15°C to 25°C. Critical irrigation stages: Crown Root Initiation (21 DAS) and Flowering.",
    "rice": "Rice requires heavy clay or alluvial soil with high water holding capacity and standing water during vegetative phases. Maintain optimal NPK of 90:50:50.",
    "fertilizer": "Apply nitrogen fertilizers (Urea) in split doses: 50% basal, 25% at tillering, and 25% at panicle/flowering initiation. Phosphatic fertilizers should be applied entirely at sowing.",
    "pest": "For initial pest infestations, apply 5% Neem Oil extract spray. For severe fungal attacks, consider Mancozeb (2g/L) or Copper Oxychloride based on local extension guidelines.",
    "yellow leaves": "Yellowing of older leaves typically indicates Nitrogen (N) deficiency. Interveinal yellowing on younger leaves suggests Iron or Magnesium deficiency.",
    "moisture": "Maintain soil moisture at field capacity (50-70%). Avoid overwatering during ripening/harvest stages to prevent fungal rot."
}

@chatbot_bp.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json() or {}
    user_question = data.get("question", "").strip()
    
    if not user_question:
        return jsonify({"error": "Question cannot be empty!"}), 400
    
    api_key = os.getenv("API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=api_key,
                base_url=os.getenv("AI_BASE_URL", "https://api.groq.com/openai/v1")
            )
            
            configured_model = os.getenv("AI_MODEL")
            candidate_models = []
            if configured_model:
                candidate_models.append(configured_model)
            candidate_models.extend(["groq/compound", "groq/compound-mini", "qwen/qwen3.6-27b"])
            
            bot_reply = None
            for model_name in candidate_models:
                try:
                    completion = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {
                                "role": "system", 
                                "content": "You are BioGrow AI, an expert agricultural consultant. Provide concise, clear, and practical advice for farmers on crops, fertilizers, irrigation, weather adaptation, and pest management."
                            },
                            {"role": "user", "content": user_question}
                        ],
                        max_tokens=450,
                        temperature=0.3
                    )
                    bot_reply = completion.choices[0].message.content
                    if bot_reply:
                        return jsonify({"response": bot_reply})
                except Exception as model_err:
                    # Try next candidate model
                    continue
        except Exception as e:
            # Fall back to knowledge base
            pass

    # Intelligent agronomic knowledge fallback
    q_lower = user_question.lower()
    matched_replies = [val for key, val in OFFLINE_KNOWLEDGE.items() if key in q_lower]
    
    if matched_replies:
        bot_reply = "🌾 " + " ".join(matched_replies)
    else:
        bot_reply = (
            "🌾 **BioGrow Farming Advisory:** For optimal crop health, monitor soil moisture weekly, "
            "perform balanced N-P-K fertilizer application based on your soil test, and use the **Leaf Doctor** "
            "tool to diagnose any foliar symptoms early. Feel free to ask about specific crops, pests, or fertilizers!"
        )
        
    return jsonify({"response": bot_reply})

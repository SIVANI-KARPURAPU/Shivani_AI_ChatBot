import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from groq import Groq


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Shivani's ChatBot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# GLOBAL PAGE STYLING
# =========================================================

st.markdown(
    """
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            background: #070a1b !important;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 15%, rgba(244, 190, 91, .13), transparent 22%),
                radial-gradient(circle at 92% 20%, rgba(144, 74, 237, .14), transparent 25%),
                #070a1b !important;
        }

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        #MainMenu,
        footer {
            display: none !important;
            visibility: hidden !important;
        }

        .block-container {
            max-width: 100% !important;
            padding: 0 !important;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0;
        }

        /* Keep the page dark during a Streamlit rerun. */
        [data-testid="stAppViewContainer"] > .main {
            background: #070a1b !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY was not found. Please check your .env file.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# Fast Groq model.
MODEL_NAME = "openai/gpt-oss-20b"


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I'm Shivani's AI assistant. 👋\n\n"
                "Ask me anything — I'm here to help you "
                "learn, explore and grow!"
            ),
        }
    ]


# =========================================================
# GEMINI
# =========================================================

SYSTEM_INSTRUCTION = """
You are Shivani's AI assistant.

Be friendly, clear, concise, and helpful.
Explain difficult concepts in simple language when appropriate.
For normal questions, avoid unnecessarily long answers.
Use short paragraphs and bullet points when useful.
"""


def build_prompt(user_message: str) -> str:
    """
    Build a compact conversation prompt.
    Keeping the history compact helps response latency.
    """
    recent = st.session_state.messages[-10:]

    history_parts = []

    for item in recent:
        role = "User" if item["role"] == "user" else "Assistant"
        history_parts.append(f"{role}: {item['content']}")

    history = "\n\n".join(history_parts)

    return (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"Conversation so far:\n{history}\n\n"
        f"User's latest message:\n{user_message}\n\n"
        "Answer the latest user message directly."
    )


def get_gemini_response(user_message: str) -> str:
    """
    Uses Groq for the AI response.
    The function name is intentionally kept unchanged so the
    remaining application code stays exactly as it is.
    """
    try:
        prompt = build_prompt(user_message)

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.7,
            max_tokens=1024,
        )

        text = (
            response.choices[0].message.content or ""
        ).strip()

        if text:
            return text

        return "I couldn't generate a response right now. Please try again."

    except Exception as error:
        print("\n========== GROQ ERROR ==========")
        print("Error type:", type(error).__name__)
        print("Error:", str(error))
        print("================================\n")

        return (
            "Sorry, I couldn't connect to Groq right now. "
            "Please try again in a moment."
        )



def process_message(user_message: str) -> None:
    user_message = user_message.strip()

    if not user_message:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    ai_response = get_gemini_response(user_message)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_response,
        }
    )


# =========================================================
# CHATBOT HTML
# =========================================================

CHATBOT_HTML = """
<div class="app-stage">

    <!-- Decorative left side -->
    <div class="side-art left-art">
        <div class="gold-orb orb-one"></div>
        <div class="purple-arc arc-one"></div>
        <div class="purple-arc arc-two"></div>

        <div class="quote-art">
            <div>Good</div>
            <div>Questions</div>
            <div>Lead to</div>
            <div>Great</div>
            <div>Things</div>
            <div class="quote-line"></div>
        </div>

        <div class="leaf leaf-one">❯</div>
        <div class="leaf leaf-two">❯</div>
    </div>


    <!-- Main chatbot -->
    <div class="chatbot-card">

        <div class="chat-header">

            <div class="brand-section">
                <div class="bot-logo">
                    <span class="bot-emoji">🤖</span>
                </div>

                <div class="brand-content">
                    <div class="brand-title">
                        Shivani's <span>ChatBot</span>
                    </div>

                    <div class="brand-tagline">
                        Your AI companion to learn, explore &amp; grow ✨
                    </div>
                </div>
            </div>

            <div class="online-section">
                <div class="online-pill">
                    <span class="online-dot"></span>
                    <span class="online-text">Online</span>
                </div>

                <div class="online-subtext">
                    Always here for you!
                </div>
            </div>

        </div>


        <div class="chat-area" id="chat-area"></div>


        <div class="typing-wrapper" id="typing-wrapper">
            <div class="bot-small-icon">🤖</div>

            <div class="typing-bubble">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>


        <div class="input-section">
            <div class="input-container">

                <div class="sparkle-icon">✦</div>

                <input
                    id="message-input"
                    type="text"
                    placeholder="Ask me anything..."
                    autocomplete="off"
                    aria-label="Message"
                />

                <button
                    id="send-button"
                    type="button"
                    aria-label="Send message"
                >
                    <svg
                        width="22"
                        height="22"
                        viewBox="0 0 24 24"
                        fill="none"
                    >
                        <path
                            d="M21 3L10.5 13.5"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                        <path
                            d="M21 3L14.5 21L10.5 13.5L3 9.5L21 3Z"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                    </svg>
                </button>

            </div>
        </div>


        <div class="chat-footer">

            <div class="footer-items">
                <span><b class="purple">▱</b> Think</span>
                <i>│</i>
                <span><b class="gold">♧</b> Learn</span>
                <i>│</i>
                <span><b class="gold">▥</b> Grow</span>
                <i>│</i>
                <span><b class="pink">♥</b> Together</span>
            </div>

            <div class="footer-line"></div>

            <div class="footer-tagline">
                Same You • Bigger Possibilities 💜
            </div>

        </div>

    </div>


    <!-- Decorative right side -->
    <div class="side-art right-art">

        <div class="right-glow"></div>

        <div class="feature-list">

            <div class="feature-item">
                <div class="feature-icon">♧</div>
                <div>
                    <strong>Learn</strong>
                    <small>New Things</small>
                </div>
            </div>

            <div class="feature-item">
                <div class="feature-icon">↗</div>
                <div>
                    <strong>Explore</strong>
                    <small>Ideas</small>
                </div>
            </div>

            <div class="feature-item">
                <div class="feature-icon">◎</div>
                <div>
                    <strong>Achieve</strong>
                    <small>Goals</small>
                </div>
            </div>

            <div class="feature-item">
                <div class="feature-icon">♡</div>
                <div>
                    <strong>Grow</strong>
                    <small>Together</small>
                </div>
            </div>

        </div>

        <div class="keep-art">
            Keep<br>
            Exploring
            <span>♡</span>
        </div>

        <div class="gold-ring ring-one"></div>
        <div class="gold-ring ring-two"></div>

    </div>

</div>
"""


# =========================================================
# CHATBOT CSS
# =========================================================

CHATBOT_CSS = """
* {
    box-sizing: border-box;
}

.app-stage {
    width: 100%;
    min-height: 100vh;

    position: relative;

    display: flex;
    align-items: center;
    justify-content: center;

    padding: 28px 34px;

    overflow: hidden;

    background:
        radial-gradient(
            circle at 5% 8%,
            rgba(242, 188, 94, .16),
            transparent 23%
        ),
        radial-gradient(
            circle at 96% 10%,
            rgba(125, 67, 227, .20),
            transparent 27%
        ),
        radial-gradient(
            circle at 50% 100%,
            rgba(120, 61, 224, .13),
            transparent 34%
        ),
        linear-gradient(
            135deg,
            #080a1c 0%,
            #10132c 46%,
            #080a1d 100%
        );

    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}


/* ---------------------------------------------------------
   BACKGROUND LIGHTS
--------------------------------------------------------- */

.app-stage::before {
    content: "";
    position: absolute;
    inset: -25%;

    background:
        radial-gradient(
            ellipse at 12% 0%,
            rgba(255, 194, 103, .20),
            transparent 18%
        ),
        radial-gradient(
            ellipse at 87% 12%,
            rgba(158, 91, 255, .18),
            transparent 20%
        );

    pointer-events: none;
}

.app-stage::after {
    content: "";
    position: absolute;
    width: 1000px;
    height: 1000px;

    border: 1px solid rgba(173, 103, 255, .11);
    border-radius: 50%;

    bottom: -780px;
    left: 50%;

    transform: translateX(-50%);
}


/* ---------------------------------------------------------
   SIDE ART
--------------------------------------------------------- */

.side-art {
    position: absolute;
    top: 0;
    bottom: 0;

    width: calc((100% - 700px) / 2);
    min-width: 180px;

    pointer-events: none;
}

.left-art {
    left: 0;
}

.right-art {
    right: 0;
}


/* gold/orange glow */
.gold-orb {
    position: absolute;
    width: 210px;
    height: 210px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(255, 206, 119, .65),
            rgba(227, 137, 69, .18) 42%,
            transparent 72%
        );

    filter: blur(2px);
}

.orb-one {
    top: -80px;
    left: -65px;
}


/* purple curved strokes */
.purple-arc {
    position: absolute;

    border-radius: 50%;

    border: 2px solid rgba(189, 119, 255, .70);

    transform: rotate(28deg);
}

.arc-one {
    width: 270px;
    height: 150px;

    top: -70px;
    left: -115px;
}

.arc-two {
    width: 340px;
    height: 190px;

    top: -78px;
    left: -130px;

    border-color: rgba(255, 203, 111, .45);
}


/* handwritten-style side message */
.quote-art {
    position: absolute;

    left: 28px;
    top: 34%;

    color: #d99aff;

    font-family:
        "Segoe Script",
        "Brush Script MT",
        cursive;

    font-size: 22px;
    line-height: 1.34;

    transform: rotate(-7deg);

    text-shadow:
        0 0 18px rgba(192, 105, 255, .30);
}

.quote-line {
    width: 85px;
    height: 2px;

    margin-top: 12px;

    background:
        linear-gradient(
            90deg,
            #d78cff,
            #f2c96d
        );

    transform: rotate(-5deg);
}


/* abstract leaves */
.leaf {
    position: absolute;

    color: rgba(113, 74, 217, .38);

    font-size: 150px;

    transform: rotate(42deg);
}

.leaf-one {
    bottom: -55px;
    left: -55px;
}

.leaf-two {
    bottom: 45px;
    left: 12px;

    font-size: 100px;
}


/* ---------------------------------------------------------
   RIGHT FEATURES
--------------------------------------------------------- */

.right-glow {
    position: absolute;

    width: 250px;
    height: 250px;

    right: -100px;
    top: 80px;

    background:
        radial-gradient(
            circle,
            rgba(126, 76, 242, .23),
            transparent 68%
        );
}

.feature-list {
    position: absolute;

    right: 32px;
    top: 29%;

    display: flex;
    flex-direction: column;

    gap: 25px;
}

.feature-item {
    display: flex;
    align-items: center;

    gap: 15px;

    color: #d6caed;

    min-width: 150px;
}

.feature-icon {
    width: 30px;

    color: #f2c96d;

    font-size: 27px;

    text-align: center;

    text-shadow:
        0 0 14px rgba(242, 201, 109, .35);
}

.feature-item strong {
    display: block;

    color: #d9ccef;

    font-size: 14px;
    font-weight: 600;
}

.feature-item small {
    display: block;

    margin-top: 3px;

    color: #9187b3;

    font-size: 11px;
}

.keep-art {
    position: absolute;

    right: 24px;
    bottom: 65px;

    color: #e4b969;

    font-family:
        "Segoe Script",
        "Brush Script MT",
        cursive;

    font-size: 20px;
    line-height: 1.2;

    transform: rotate(-8deg);

    text-align: center;

    text-shadow:
        0 0 15px rgba(239, 190, 91, .25);
}

.keep-art span {
    display: block;

    margin-top: 5px;

    color: #d995ff;

    font-size: 25px;
}


/* Decorative bottom curves */
.gold-ring {
    position: absolute;

    border: 1px solid rgba(244, 197, 107, .42);
    border-radius: 50%;
}

.ring-one {
    width: 260px;
    height: 100px;

    right: -100px;
    bottom: -25px;

    transform: rotate(-24deg);
}

.ring-two {
    width: 330px;
    height: 125px;

    right: -120px;
    bottom: -48px;

    border-color: rgba(172, 94, 255, .38);

    transform: rotate(-24deg);
}


/* ---------------------------------------------------------
   MAIN CARD
--------------------------------------------------------- */

.chatbot-card {
    width: 560px;
    height: 760px;

    max-width: 100%;

    position: relative;
    z-index: 5;

    display: flex;
    flex-direction: column;

    overflow: hidden;

    background:
        radial-gradient(
            circle at 50% 0%,
            rgba(151, 80, 255, .14),
            transparent 35%
        ),
        rgba(13, 17, 39, .97);

    border:
        1px solid rgba(202, 127, 255, .74);

    border-radius: 28px;

    box-shadow:
        0 0 0 1px rgba(255, 212, 130, .08),
        0 25px 90px rgba(0, 0, 0, .65),
        0 0 55px rgba(127, 62, 224, .18);
}


/* ---------------------------------------------------------
   HEADER
--------------------------------------------------------- */

.chat-header {
    height: 112px;
    min-height: 112px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 18px 24px;

    background:
        linear-gradient(
            135deg,
            rgba(27, 29, 60, .98),
            rgba(17, 21, 46, .98)
        );

    border-bottom:
        1px solid rgba(198, 125, 255, .28);
}

.brand-section {
    display: flex;
    align-items: center;

    gap: 14px;

    min-width: 0;
}

.bot-logo {
    width: 58px;
    height: 58px;

    flex-shrink: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 18px;

    background:
        linear-gradient(
            145deg,
            #6746b5,
            #a852e8
        );

    border:
        1px solid rgba(255, 221, 143, .46);

    box-shadow:
        0 0 25px rgba(151, 76, 237, .34);
}

.bot-emoji {
    font-size: 32px;
    line-height: 1;
}

.brand-content {
    min-width: 0;
}

.brand-title {
    color: #fff;

    font-size: 22px;
    font-weight: 760;

    line-height: 1.1;

    letter-spacing: -.4px;
}

.brand-title span {
    color: #d58aff;

    text-shadow:
        0 0 16px rgba(204, 113, 255, .25);
}

.brand-tagline {
    margin-top: 7px;

    color: #c5b7e6;

    font-size: 11.5px;
}

.online-section {
    display: flex;
    flex-direction: column;

    align-items: flex-end;

    gap: 6px;
}

.online-pill {
    display: flex;
    align-items: center;

    gap: 8px;

    padding: 8px 14px;

    border-radius: 20px;

    background:
        rgba(44, 71, 67, .40);

    border:
        1px solid rgba(104, 224, 169, .36);
}

.online-dot {
    width: 9px;
    height: 9px;

    border-radius: 50%;

    background: #62e6a4;

    box-shadow:
        0 0 10px rgba(98, 230, 164, .9);
}

.online-text {
    color: #7be7b0;

    font-size: 14px;
    font-weight: 700;
}

.online-subtext {
    color: #9389b1;
    font-size: 9px;
}


/* ---------------------------------------------------------
   CHAT AREA
--------------------------------------------------------- */

.chat-area {
    flex: 1;

    min-height: 0;

    overflow-y: auto;

    padding: 24px 23px 18px;

    background:
        radial-gradient(
            circle at 80% 15%,
            rgba(126, 66, 218, .07),
            transparent 28%
        ),
        #0c1125;
}

.chat-area::-webkit-scrollbar {
    width: 6px;
}

.chat-area::-webkit-scrollbar-track {
    background: transparent;
}

.chat-area::-webkit-scrollbar-thumb {
    background:
        linear-gradient(
            #7249c1,
            #a45ce6
        );

    border-radius: 10px;
}

.message-row {
    display: flex;

    align-items: flex-end;

    gap: 9px;

    margin-bottom: 18px;
}

.message-row.user {
    justify-content: flex-end;
}

.message-bot-icon,
.bot-small-icon {
    width: 32px;
    height: 32px;

    flex-shrink: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 10px;

    background: #28214a;

    border:
        1px solid rgba(180, 114, 255, .28);

    font-size: 17px;
}

.message-bubble {
    max-width: 78%;

    padding: 12px 15px;

    border-radius: 16px;

    font-size: 13px;
    line-height: 1.55;

    color: #eeeafd;

    word-break: break-word;
}

.message-row.ai .message-bubble {
    background:
        linear-gradient(
            145deg,
            #202543,
            #191e39
        );

    border:
        1px solid rgba(167, 126, 232, .18);

    border-bottom-left-radius: 5px;

    box-shadow:
        0 7px 20px rgba(0, 0, 0, .15);
}

.message-row.user .message-bubble {
    color: white;

    background:
        linear-gradient(
            135deg,
            #a044ee,
            #7249df
        );

    border:
        1px solid rgba(216, 171, 255, .25);

    border-bottom-right-radius: 5px;

    box-shadow:
        0 8px 25px rgba(107, 63, 201, .25);
}


/* ---------------------------------------------------------
   TYPING
--------------------------------------------------------- */

.typing-wrapper {
    display: none;

    align-items: flex-end;

    gap: 9px;

    padding: 0 23px 10px;

    background: #0c1125;
}

.typing-bubble {
    width: 68px;
    height: 37px;

    display: flex;
    align-items: center;
    justify-content: center;

    gap: 5px;

    border-radius: 15px;
    border-bottom-left-radius: 5px;

    background: #202543;

    border:
        1px solid rgba(167, 126, 232, .18);
}

.typing-bubble span {
    width: 6px;
    height: 6px;

    border-radius: 50%;

    background: #c08dff;

    animation:
        typing-animation 1.2s infinite ease-in-out;
}

.typing-bubble span:nth-child(2) {
    animation-delay: .15s;
}

.typing-bubble span:nth-child(3) {
    animation-delay: .30s;
}

@keyframes typing-animation {
    0%, 60%, 100% {
        transform: translateY(0);
        opacity: .45;
    }

    30% {
        transform: translateY(-4px);
        opacity: 1;
    }
}


/* ---------------------------------------------------------
   INPUT
--------------------------------------------------------- */

.input-section {
    flex-shrink: 0;

    padding: 15px 20px 12px;

    background: #0c1125;
}

.input-container {
    height: 56px;

    display: flex;
    align-items: center;

    gap: 9px;

    padding: 5px 6px 5px 14px;

    border-radius: 18px;

    background: #11172f;

    border:
        1.5px solid rgba(207, 130, 255, .80);

    box-shadow:
        0 0 20px rgba(146, 74, 222, .08);

    transition: .2s ease;
}

.input-container:focus-within {
    border-color: #dc91ff;

    box-shadow:
        0 0 0 3px rgba(155, 80, 228, .10),
        0 0 25px rgba(155, 80, 228, .12);
}

.sparkle-icon {
    flex-shrink: 0;

    color: #f3ce77;

    font-size: 21px;
}

#message-input {
    flex: 1;

    min-width: 0;

    border: none;
    outline: none;

    background: transparent;

    color: #f5f1ff;

    font-size: 13px;
}

#message-input::placeholder {
    color: #918aa9;
}

#send-button {
    width: 44px;
    height: 44px;

    flex-shrink: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    border: none;
    border-radius: 50%;

    cursor: pointer;

    color: white;

    background:
        linear-gradient(
            135deg,
            #aa4df1,
            #7350e8
        );

    box-shadow:
        0 5px 18px rgba(139, 68, 225, .35);

    transition:
        transform .18s ease,
        box-shadow .18s ease;
}

#send-button:hover {
    transform: translateY(-2px);

    box-shadow:
        0 8px 22px rgba(139, 68, 225, .48);
}

#send-button:active {
    transform: scale(.95);
}

#send-button:disabled {
    opacity: .55;
    cursor: default;
    transform: none;
}


/* ---------------------------------------------------------
   FOOTER
--------------------------------------------------------- */

.chat-footer {
    flex-shrink: 0;

    padding: 8px 20px 18px;

    text-align: center;

    background: #0c1125;
}

.footer-items {
    display: flex;
    align-items: center;
    justify-content: center;

    gap: 11px;

    color: #aaa4c1;

    font-size: 10px;
}

.footer-items i {
    color: #514c68;
    font-style: normal;
}

.gold {
    color: #f2c96d;
}

.purple {
    color: #d183ff;
}

.pink {
    color: #f38cc7;
}

.footer-line {
    width: 55px;
    height: 1px;

    margin: 11px auto 8px;

    background:
        linear-gradient(
            90deg,
            transparent,
            #e3b967,
            transparent
        );
}

.footer-tagline {
    color: #9d91c4;

    font-size: 9.5px;

    letter-spacing: .2px;
}


/* ---------------------------------------------------------
   RESPONSIVE
--------------------------------------------------------- */

@media (max-width: 1050px) {
    .side-art {
        display: none;
    }
}

@media (max-width: 620px) {
    .app-stage {
        padding: 0;
    }

    .chatbot-card {
        width: 100%;
        height: 100vh;
        min-height: 600px;

        border-radius: 0;

        border-left: none;
        border-right: none;
    }
}

@media (max-height: 820px) and (min-width: 621px) {
    .chatbot-card {
        height: 700px;
    }
}
"""


# =========================================================
# CHATBOT JAVASCRIPT
# =========================================================

CHATBOT_JS = """
export default function(component) {

    const {
        parentElement,
        data,
        setTriggerValue
    } = component;

    const chatArea =
        parentElement.querySelector("#chat-area");

    const input =
        parentElement.querySelector("#message-input");

    const sendButton =
        parentElement.querySelector("#send-button");

    const typingWrapper =
        parentElement.querySelector("#typing-wrapper");

    if (!chatArea || !input || !sendButton || !typingWrapper) {
        return;
    }


    function escapeHTML(text) {
        const div = document.createElement("div");
        div.textContent = String(text ?? "");
        return div.innerHTML;
    }


    function formatMessage(text) {
        return escapeHTML(text).replace(/\\n/g, "<br>");
    }


    function scrollToBottom() {
        requestAnimationFrame(() => {
            chatArea.scrollTop = chatArea.scrollHeight;
        });
    }


    function renderMessages(messages) {

        chatArea.innerHTML = "";

        if (!Array.isArray(messages)) {
            return;
        }

        messages.forEach(message => {

            const row =
                document.createElement("div");

            if (message.role === "user") {

                row.className =
                    "message-row user";

                const bubble =
                    document.createElement("div");

                bubble.className =
                    "message-bubble";

                bubble.innerHTML =
                    formatMessage(message.content);

                row.appendChild(bubble);

            } else {

                row.className =
                    "message-row ai";

                const botIcon =
                    document.createElement("div");

                botIcon.className =
                    "message-bot-icon";

                botIcon.textContent = "🤖";

                const bubble =
                    document.createElement("div");

                bubble.className =
                    "message-bubble";

                bubble.innerHTML =
                    formatMessage(message.content);

                row.appendChild(botIcon);
                row.appendChild(bubble);
            }

            chatArea.appendChild(row);
        });

        scrollToBottom();
    }


    function sendMessage() {

        const message =
            input.value.trim();

        if (!message || sendButton.disabled) {
            return;
        }


        // Show user message immediately.
        const row =
            document.createElement("div");

        row.className =
            "message-row user";

        const bubble =
            document.createElement("div");

        bubble.className =
            "message-bubble";

        bubble.innerHTML =
            formatMessage(message);

        row.appendChild(bubble);

        chatArea.appendChild(row);


        // Clear input.
        input.value = "";


        // Show typing animation immediately.
        typingWrapper.style.display = "flex";

        sendButton.disabled = true;

        scrollToBottom();


        // Send event to Python.
        setTriggerValue(
            "send_message",
            message
        );
    }


    sendButton.onclick = sendMessage;


    input.onkeydown = function(event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();
        }
    };


    // Python -> browser update.
    renderMessages(data?.messages || []);


    if (data?.loading) {

        typingWrapper.style.display = "flex";
        sendButton.disabled = true;

    } else {

        typingWrapper.style.display = "none";
        sendButton.disabled = false;
    }


    scrollToBottom();
}
"""


# =========================================================
# CUSTOM COMPONENT
# =========================================================

chatbot_component = st.components.v2.component(
    name="shivani_chatbot_final",
    html=CHATBOT_HTML,
    css=CHATBOT_CSS,
    js=CHATBOT_JS,
)


# =========================================================
# CHATBOT FRAGMENT
# =========================================================
#
# Streamlit 1.63 supports fragments. The chatbot lives in a
# fragment so the decorative page and outer app do not need
# to be reconstructed on every message event.
# =========================================================

@st.fragment(key="chatbot_fragment")
def render_chatbot():

    with st.container(
        horizontal=True,
        horizontal_alignment="center",
        vertical_alignment="center",
        gap=None,
    ):

        result = chatbot_component(
            data={
                "messages": st.session_state.messages,
                "loading": False,
            },
            on_send_message_change=lambda: None,
            key="shivani_chatbot_instance",
            width=1260,
            height=820,
        )

    if result.send_message:

        process_message(result.send_message)

        # Only rerun this chatbot fragment, not the full app.
        st.rerun(scope="fragment")


render_chatbot()

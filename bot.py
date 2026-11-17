import asyncio
import sqlite3
from datetime import date
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
cSg
TOKEN = "9250802706:AAHm-xFZ2Ks_Kd63IYaLxcSMGMJ5tu-dcSg"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- BAZA BILAN ISHLASH ---
def db_start():
    conn = sqlite3.connect("quiz_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            fullname TEXT,
            score INTEGER DEFAULT 0,
            questions_answered INTEGER DEFAULT 0,
            last_active_date TEXT
        )
    """)
    conn.commit()
    conn.close()

db_start()

class QuizState(StatesGroup):
    waiting_for_name = State()
    answering = State()

# 7-sinf matematika bo'yicha 75 ta savoldan iborat baza
QUESTIONS = [
    {"question": "1) (-3)^2 + 4 * 2 ni hisoblang:", "options": ["17", "1", "25", "-1"], "correct": 0},
    {"question": "2) 3x - 5 = 10 tenglamani yeching:", "options": ["5", "3", "4", "6"], "correct": 0},
    {"question": "3) Bir xil asosli darajalarni ko'paytirganda ko'rsatkichlar nima qilinadi?", "options": ["Qo'shiladi", "Ayiriladi", "Ko'paytiriladi", "Bo'linadi"], "correct": 0},
    {"question": "4) 60 ning 20% ​​ni toping:", "options": ["12", "10", "15", "20"], "correct": 0},
    {"question": "5) Kvadratning tomoni 5 sm bo'lsa, uning yuzini toping:", "options": ["25 sm²", "20 sm²", "10 sm²", "30 sm²"], "correct": 0},
    {"question": "6) (-2)^3 qiymatini toping:", "options": ["-8", "8", "-6", "6"], "correct": 0},
    {"question": "7) 0.5 sonining teskari sonini toping:", "options": ["2", "-2", "0.2", "1"], "correct": 0},
    {"question": "8) Ushbu ifodani soddalashtiring: 2a + 3a - a", "options": ["4a", "5a", "6a", "3a"], "correct": 0},
    {"question": "9) To'g'ri burchakning necha foizi 45 gradusni tashkil qiladi?", "options": ["50%", "25%", "75%", "100%"], "correct": 0},
    {"question": "10) 12 va 18 sonlarining eng kichik umumiy karralisini (EKUK) toping:", "options": ["36", "6", "72", "24"], "correct": 0},
    {"question": "11) Moduldan chiqqan son qanday ishoraga ega bo'ladi?", "options": ["Faqat musbat (yoki 0)", "Faqat manfiy", "Farqi yo'q", "Faqat 1"], "correct": 0},
    {"question": "12) 3x + 2 = 2x + 7 tenglamani yeching:", "options": ["5", "3", "2", "7"], "correct": 0},
    {"question": "13) Doiraning radiusi 4 sm bo'lsa, uning diametri nechaga teng?", "options": ["8 sm", "2 sm", "16 sm", "6 sm"], "correct": 0},
    {"question": "14) 2/3 va 4/5 qaysi biri katta?", "options": ["4/5", "2/3", "Teng", "Aniqlab bo'lmaydi"], "correct": 0},
    {"question": "15) Agar a = -3 bo'lsa, a^2 - 5 ning qiymatini toping:", "options": ["4", "14", "-14", "-4"], "correct": 0},
    {"question": "16) 1 soatning 15 daqiqasi necha qismini tashkil qiladi?", "options": ["1/4", "1/3", "1/2", "1/5"], "correct": 0},
    {"question": "17) Proportsiyaning asosiy xossasi nima?", "options": ["Chetki hadlar ko'paytmasi o'rta hadlar ko'paytmasiga teng", "Qo'shiladi", "Bo'linadi", "Farqi yo'q"], "correct": 0},
    {"question": "18) 100 sonining natural bo'luvchilari soni nechta?", "options": ["9 ta", "6 ta", "8 ta", "10 ta"], "correct": 0},
    {"question": "19) Uchburchakning ichki burchaklari yig'indisi nechiga teng?", "options": ["180°", "360°", "90°", "270°"], "correct": 0},
    {"question": "20) 0 ga bo'lish mumkinmi?", "options": ["Mumkin emas", "Mumkin, natija 0", "Mumkin, natija cheksizlik", "Faqat musbat sondagina"], "correct": 0},
    {"question": "21) 7 ning kubi nechiga teng?", "options": ["343", "49", "21", "243"], "correct": 0},
    {"question": "22) Ikki sonning yig'indisi 20, ulardan biri x bo'lsa, ikkinchisi nimaga teng?", "options": ["20 - x", "x - 20", "20x", "x / 20"], "correct": 0},
    {"question": "23) 0.25 ni oddiy kasr ko'rinishida yozing:", "options": ["1/4", "1/2", "2/5", "1/3"], "correct": 0},
    {"question": "24) Kubning nechta qirrasi bor?", "options": ["12", "8", "6", "4"], "correct": 0},
    {"question": "25) (-1)^100 qiymati nechaga teng?", "options": ["1", "-1", "100", "-100"], "correct": 0},
    {"question": "26) Ikki manfiy sonni ko'paytirganda qanday ishora hosil bo'ladi?", "options": ["Musbat", "Manfiy", "Nol", "O'zgarmaydi"], "correct": 0},
    {"question": "27) 45 minut 1 soatning necha foizini tashkil qiladi?", "options": ["75%", "50%", "60%", "80%"], "correct": 0},
    {"question": "28) Agar x = -5 bo'lsa, |-x| nimaga teng?", "options": ["5", "-5", "0", "25"], "correct": 0},
    {"question": "29) 18 va 24 sonlarining eng katta umumiy bo'luvchisini (EKUB) toping:", "options": ["6", "3", "12", "2"], "correct": 0},
    {"question": "30) To'g'ri to'rtburchakning eni 4 sm, bo'yi 7 sm. Perimetrini toping:", "options": ["22 sm", "28 sm", "11 sm", "14 sm"], "correct": 0},
    {"question": "31) Hisoblang: 2^5", "options": ["32", "16", "64", "10"], "correct": 0},
    {"question": "32) (-5) * (-6) ni toping:", "options": ["30", "-30", "11", "-11"], "correct": 0},
    {"question": "33) 120 ning 50% ni toping:", "options": ["60", "30", "90", "40"], "correct": 0},
    {"question": "34) Ikki natural sonning EKUBi 1 ga teng bo'lsa, ular nima deyiladi?", "options": ["O'zaro tub sonlar", "Tub sonlar", "Juft sonlar", "Murakkab sonlar"], "correct": 0},
    {"question": "35) 3(x - 2) = 12 tenglamani yeching:", "options": ["6", "5", "4", "7"], "correct": 0},
    {"question": "36) Ko'phadni ko'paytuvchilarga ajrating: a^2 - b^2", "options": ["(a-b)(a+b)", "(a-b)^2", "(a+b)^2", "a(a-b)"], "correct": 0},
    {"question": "37) Aylananing uzunligini topish formulasi qaysi?", "options": ["C = 2 * pi * r", "C = pi * r^2", "C = 4 * a", "C = a * b"], "correct": 0},
    {"question": "38) (-4)^2 ning qiymati nechaga teng?", "options": ["16", "-16", "8", "-8"], "correct": 0},
    {"question": "39) 0.1 * 0.01 ni hisoblang:", "options": ["0.001", "0.01", "0.1", "1"], "correct": 0},
    {"question": "40) Agar x = 2 va y = 3 bo'lsa, 2x + 3y qiymatini toping:", "options": ["13", "12", "10", "15"], "correct": 0},
    {"question": "41) 500 sonining 10% ini toping:", "options": ["50", "5", "500", "25"], "correct": 0},
    {"question": "42) Ikki to'g'ri chiziq kesishganda nechta vertikal burchak hosil bo'ladi?", "options": ["2 ta", "4 ta", "1 ta", "Cheksiz"], "correct": 0},
    {"question": "43) 1 tonna necha kilogramm?", "options": ["1000 kg", "100 kg", "10 kg", "10000 kg"], "correct": 0},
    {"question": "44) 4x + 8 = 20 tenglamadagi x ning qiymatini toping:", "options": ["3", "4", "2", "5"], "correct": 0},
    {"question": "45) 3/4 kasrni o'nli kasrga aylantiring:", "options": ["0.75", "0.5", "0.25", "0.8"], "correct": 0},
    {"question": "46) 1 dan 50 gacha bo'lgan sonlar ichida nechta tub son bor?", "options": ["15 ta", "10 ta", "20 ta", "12 ta"], "correct": 0},
    {"question": "47) Teng yonli uchburchakning asosidagi burchaklari qanday?", "options": ["O'zaro teng", "Har xil", "To'g'ri burchak", "O'tmas burchak"], "correct": 0},
    {"question": "48) Paralelepipedning nechta uchi bor?", "options": ["8 ta", "6 ta", "12 ta", "4 ta"], "correct": 0},
    {"question": "49) (-15) / 3 ni hisoblang:", "options": ["-5", "5", "-3", "3"], "correct": 0},
    {"question": "50) 80 ning 3/4 qismini toping:", "options": ["60", "40", "20", "50"], "correct": 0},
    {"question": "51) Kvadratning perimetri 36 sm. Uning tomonini toping:", "options": ["9 sm", "6 sm", "12 sm", "18 sm"], "correct": 0},
    {"question": "52) 2x^2 * 3x^3 ni soddalashtiring:", "options": ["6x^5", "5x^5", "6x^6", "5x^6"], "correct": 0},
    {"question": "53) 0 soni qaysi songa bo'linmaydi?", "options": ["0 ga", "1 ga", "Barcha songa", "Manfiy songa"], "correct": 0},
    {"question": "54) Ikki qo'shni burchaklar yig'indisi nechiga teng?", "options": ["180°", "90°", "360°", "270°"], "correct": 0},
    {"question": "55) 1 litr suv necha kub santimetrga teng?", "options": ["1000 sm³", "100 sm³", "10000 sm³", "10 sm³"], "correct": 0},
    {"question": "56) (-7) + 15 ni hisoblang:", "options": ["8", "-8", "22", "-22"], "correct": 0},
    {"question": "57) 144 sonining kvadrat ildizi nechiga teng?", "options": ["12", "14", "16", "11"], "correct": 0},
    {"question": "58) 5x - 3 = 2x + 9 tenglamani yeching:", "options": ["4", "3", "5", "2"], "correct": 0},
    {"question": "59) To'g'ri burchakli uchburchakning gipotenuzasi nimaga nisbatan eng kattadir?", "options": ["Katetlarga nisbatan", "Burchaklarga nisbatan", "Perimetrga nisbatan", "Hech qanday"], "correct": 0},
    {"question": "60) 2.5 * 4 ni hisoblang:", "options": ["10", "8", "12", "9"], "correct": 0},
    {"question": "61) 36 ning 25% ini toping:", "options": ["9", "6", "12", "15"], "correct": 0},
    {"question": "62) (-2)^4 qiymatini toping:", "options": ["16", "-16", "8", "-8"], "correct": 0},
    {"question": "63) 10 ga bo'lganda qoldiq 3 qoladigan eng kichik ikki xonali sonni toping:", "options": ["13", "23", "33", "3"], "correct": 0},
    {"question": "64) Uchburchakning yuzini topish formulasi qaysi?", "options": ["S = (a * h) / 2", "S = a * b", "S = 4 * a", "S = a^3"], "correct": 0},
    {"question": "65) 0.04 sonining kvadrat ildizini toping:", "options": ["0.2", "0.4", "0.02", "2"], "correct": 0},
    {"question": "66) 7x = 56 tenglamani yeching:", "options": ["8", "7", "9", "6"], "correct": 0},
    {"question": "67) 1 soat 20 minut necha minut?", "options": ["80 minut", "70 minut", "90 minut", "60 minut"], "correct": 0},
    {"question": "68) Ikki o'zaro teskari sonlarning ko'paytmasi nechiga teng?", "options": ["1", "0", "-1", "Aniqlanmagan"], "correct": 0},
    {"question": "69) 99 ning raqamlari yig'indisi nechiga teng?", "options": ["18", "9", "81", "0"], "correct": 0},
    {"question": "70) Doiraning yuzini topish formulasi qaysi?", "options": ["S = pi * r^2", "S = 2 * pi * r", "S = 4 * pi * r", "S = r^2"], "correct": 0},
    {"question": "71) 1/2 + 1/4 ni hisoblang:", "options": ["3/4", "2/6", "1/6", "2/4"], "correct": 0},
    {"question": "72) (-8) - (-5) ni hisoblang:", "options": ["-3", "-13", "3", "13"], "correct": 0},
    {"question": "73) 15 ning kvadrati nechiga teng?", "options": ["225", "215", "196", "250"], "correct": 0},
    {"question": "74) 6x - 10 = 2x + 18 tenglamani yeching:", "options": ["7", "6", "8", "5"], "correct": 0},
    {"question": "75) 500 kg necha t (tonna)?", "options": ["0.5 t", "5 t", "0.05 t", "50 t"], "correct": 0}
]

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🧠 Bugungi testni boshlash")
    builder.button(text="📊 Reyting")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    conn = sqlite3.connect("quiz_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT fullname FROM users WHERE user_id = ?", (message.from_user.id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        await message.answer(f"Salom, {user[0]}! Kunlik testlarni bajarish uchun pastdagi tugmani bosing:", reply_markup=get_main_menu())
    else:
        await message.answer("Salom! 7-sinf matematika **75 kunlik / 15 kunlik marafon** reyting botiga xush kelibsiz.\n\n🏆 *15 kundan keyin yakuniy reytingda 1-o'rinni egallagan ishtirokchiga pul mukofoti beriladi!*\n\nIltimos, ism va familiyangizni kiriting (masalan: *Azizbek Anvarov*):")
        await state.set_state(QuizState.waiting_for_name)

@dp.message(QuizState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    fullname = message.text.strip()
    
    conn = sqlite3.connect("quiz_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, fullname, score, questions_answered, last_active_date) 
        VALUES (?, ?, 0, 0, '')
    """, (message.from_user.id, fullname))
    conn.commit()
    conn.close()

    await state.clear()
    await message.answer(f"Rahmat, {fullname}! Ma'lumotlaringiz saqlandi. G‘olib uchun **pul mukofoti** o‘ynalmoqda, omad tilaymiz!", reply_markup=get_main_menu())

@dp.message(F.text == "📊 Reyting")
async def show_rating(message: types.Message):
    conn = sqlite3.connect("quiz_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT fullname, score, questions_answered FROM users ORDER BY score DESC, questions_answered ASC LIMIT 10")
    top_users = cursor.fetchall()
    conn.close()

    if not top_users:
        await message.answer("Hozircha reyting bo'sh.")
    else:
        text = "🏆 **7-sinf Matematika Reytingi:**\n*(1-o'ringa pul mukofoti beriladi! 💰)*\n\n"
        for i, (name, score, q_ans) in enumerate(top_users, start=1):
            text += f"{i}. {name} — **{score} ball** (Ishlagan: {q_ans}/75)\n"
        await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🧠 Bugungi testni boshlash")
async def start_daily_quiz(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    today_str = str(date.today())

    conn = sqlite3.connect("quiz_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT questions_answered, last_active_date FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()

    if not res:
        await message.answer("Iltimos, avval /start buyrug'ini bosing va ro'yxatdan o'ting.")
        return

    q_answered, last_date = res

    # Hammasi tugaganmi tekshirish (75 ta savol)
    if q_answered >= 75:
        await message.answer("🎉 Tabriklaymiz! Siz barcha 75 ta savolni to'liq ishlab bo'ldingiz. 1-o'rin uchun kurash yakunlandi, reytingni kuzatib boring! 💰")
        return

    # Bugun allaqachon ishlaganmi tekshirish
    if last_date == today_str:
        await message.answer("⏳ Siz bugungi 5 ta savolni allaqachon ishlab bo'lgansiz. Yangi savollar ertaga chiqadi!")
        return

    # Hozirgi kunda ishlanadigan 5 ta savolning boshlang'ich indeksi
    await state.update_data(session_index=0, session_correct=0, current_q_count=0)
    await send_next_daily_question(message, state, q_answered)

async def send_next_daily_question(message_or_callback, state: FSMContext, current_global_index):
    data = await state.get_data()
    session_count = data.get("current_q_count", 0)

    # Agar bugungi 5 ta savol tugagan bo'lsa
    if session_count >= 5 or current_global_index >= 75:
        user_id = message_or_callback.from_user.id if isinstance(message_or_callback, types.Message) else message_or_callback.from_user.id
        today_str = str(date.today())
        session_correct = data.get("session_correct", 0)

        # Bazani yangilash
        conn = sqlite3.connect("quiz_bot.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET score = score + ?, 
                questions_answered = questions_answered + ?, 
                last_active_date = ? 
            WHERE user_id = ?
        """, (session_correct, session_count, today_str, user_id))
        conn.commit()
        conn.close()

        text = f"✅ **Bugungi 5 ta savol yakunlandi!**\nSiz bugun {session_correct} ta to'g'ri javob topdingiz.\n\nErtaga yangi 5 ta savol ochiladi! Pul mukofoti uchun olg'a! 💰"
        
        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(text, reply_markup=get_main_menu(), parse_mode="Markdown")
        else:
            await message_or_callback.message.answer(text, reply_markup=get_main_menu(), parse_mode="Markdown")
            await message_or_callback.message.delete()
            
        await state.clear()
        return

    q = QUESTIONS[current_global_index]
    builder = InlineKeyboardBuilder()
    for i, option in enumerate(q["options"]):
        builder.button(text=option, callback_data=f"daily_{current_global_index}_{i}")
    builder.adjust(2)

    text = f"<b>{q['question']}</b>\n\n*(Bugungi savol: {session_count + 1}/5)*"

    if isinstance(message_or_callback, types.Message):
        await message_or_callback.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await message_or_callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")

    await state.set_state(QuizState.answering)

@dp.callback_query(F.data.startswith("daily_"))
async def process_daily_answer(callback: types.CallbackQuery, state: FSMContext):
    data_parts = callback.data.split("_")
    global_index = int(data_parts[1])
    selected_option = int(data_parts[2])

    q = QUESTIONS[global_index]
    state_data = await state.get_data()
    session_correct = state_data.get("session_correct", 0)
    current_q_count = state_data.get("current_q_count", 0)

    if selected_option == q["correct"]:
        session_correct += 1
        await callback.answer("✅ To'g'ri! (+1 ball)")
    else:
        await callback.answer("❌ Noto'g'ri! (0 ball)")

    current_q_count += 1
    await state.update_data(session_correct=session_correct, current_q_count=current_q_count)

    # Keyingi savolga o'tish
    await send_next_daily_question(callback, state, global_index + 1)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
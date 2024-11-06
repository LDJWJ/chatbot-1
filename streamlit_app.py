# pip install SpeechRecognition
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import random
import time
import difflib
from googletrans import Translator

def initialize_session_state():
    """세션 상태 초기화"""
    if 'current_word' not in st.session_state:
        st.session_state.current_word = ''
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'total_attempts' not in st.session_state:
        st.session_state.total_attempts = 0
    if 'selected_gender' not in st.session_state:
        st.session_state.selected_gender = '남자아이'

def get_random_word():
    """무작위 단어 선택"""
    words = [
        "apple", "banana", "orange", "grape", "strawberry",
        "computer", "python", "programming", "artificial", "intelligence",
        "beautiful", "wonderful", "amazing", "fantastic", "excellent"
    ]
    return random.choice(words)

def create_audio(text, gender):
    """텍스트를 음성으로 변환 (성별에 따른 설정 적용)"""
    # 성별에 따른 언어 설정
    if gender == '남자아이':
        tts = gTTS(text=text, lang='en', tld='co.uk')  # 영국 영어 (남성스러운 음색)
    else:
        tts = gTTS(text=text, lang='en', tld='com')    # 미국 영어 (여성스러운 음색)
    
    filename = "word.mp3"
    tts.save(filename)
    return filename

def speech_to_text():
    """음성을 텍스트로 변환"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("말씀해주세요...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            text = r.recognize_google(audio, language='en-US')
            return text.lower()
        except sr.WaitTimeoutError:
            st.error("음성이 감지되지 않았습니다. 다시 시도해주세요.")
            return None
        except sr.UnknownValueError:
            st.error("음성을 인식할 수 없습니다. 다시 시도해주세요.")
            return None
        except sr.RequestError:
            st.error("음성 인식 서비스에 접근할 수 없습니다.")
            return None

def calculate_similarity(word1, word2):
    """두 단어의 유사도 계산"""
    return difflib.SequenceMatcher(None, word1, word2).ratio()

def get_character_emoji(gender):
    """성별에 따른 이모지 반환"""
    return "👦" if gender == '남자아이' else "👧"

def main():
    st.title("📢 발음 체크 앱")
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # 상단에 성별 선택 라디오 버튼 추가
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        selected_gender = st.radio(
            "캐릭터를 선택하세요:",
            options=['남자아이', '여자아이'],
            horizontal=True,
            key='gender_selection'
        )
    with col2:
        st.write(f"### {get_character_emoji(selected_gender)}")
    
    # 선택된 성별 저장
    st.session_state.selected_gender = selected_gender
    
    # 구분선 추가
    st.markdown("---")
    
    # 사이드바에 점수 표시
    st.sidebar.header("점수")
    st.sidebar.write(f"정확도: {st.session_state.score}/{st.session_state.total_attempts if st.session_state.total_attempts > 0 else 1:.2%}")
    
    # 새 단어 받기 버튼
    if st.button("새 단어 받기"):
        st.session_state.current_word = get_random_word()
        audio_file = create_audio(st.session_state.current_word, st.session_state.selected_gender)
        
        # 단어와 발음 듣기 버튼 표시
        st.write(f"## 이 단어를 읽어보세요: **{st.session_state.current_word}**")
        st.audio(audio_file)
        
        # 한국어 의미 표시
        translator = Translator()
        try:
            korean_meaning = translator.translate(st.session_state.current_word, dest='ko').text
            st.write(f"단어 뜻: {korean_meaning}")
        except:
            st.write("단어 뜻을 가져올 수 없습니다.")
        
        # 임시 파일 삭제
        os.remove(audio_file)
    
    # 발음 체크 버튼
    if st.button("발음 체크하기"):
        if st.session_state.current_word:
            spoken_text = speech_to_text()
            if spoken_text:
                similarity = calculate_similarity(st.session_state.current_word, spoken_text)
                st.session_state.total_attempts += 1
                
                if similarity > 0.8:
                    st.success(f"정확합니다! (유사도: {similarity:.2%})")
                    st.session_state.score += 1
                    st.balloons()  # 성공시 풍선 효과 추가
                else:
                    st.error(f"다시 시도해보세요. 인식된 단어: {spoken_text} (유사도: {similarity:.2%})")
                
                # 결과 표시
                st.write(f"당신이 말한 단어: {spoken_text}")
                st.write(f"목표 단어: {st.session_state.current_word}")
        else:
            st.warning("먼저 '새 단어 받기' 버튼을 클릭하세요.")
    
    # 도움말
    with st.expander("사용 방법"):
        st.write("""
        1. 상단에서 캐릭터(남자아이/여자아이)를 선택하세요.
        2. '새 단어 받기' 버튼을 클릭하여 새로운 단어를 받습니다.
        3. 단어의 발음을 들어보려면 재생 버튼을 클릭하세요.
        4. '발음 체크하기' 버튼을 클릭하고 단어를 말해보세요.
        5. 결과를 확인하고 점수를 높여보세요!
        """)

if __name__ == "__main__":
    main()

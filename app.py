import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# เก็บสถานะระบบและผลลัพธ์
game_state = {
    "is_active": False,
    "results": []
}

@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

# อาจารย์สั่งเริ่มเกม
@socketio.on('start_game')
def handle_start():
    game_state["is_active"] = False
    game_state["results"] = []
    emit('reset_game', broadcast=True)
    emit('start_countdown', broadcast=True)

# เมื่อนับถอยหลังจบ ปลดล็อกปุ่ม
@socketio.on('enable_buttons')
def handle_enable():
    game_state["is_active"] = True

# นักเรียนกดปุ่ม
@socketio.on('press_button')
def handle_press(data):
    if not game_state["is_active"]:
        return
    
    student_name = data.get('name', 'Anonymous')
    press_time = time.time()  # timestamp ความละเอียดวินาที (มีทศนิยม)
    
    # ตรวจสอบว่าเคยกดไปแล้วหรือยัง (กดได้คนละ 1 ครั้งต่อรอบ)
    if not any(r['name'] == student_name for r in game_state["results"]):
        game_state["results"].append({
            "name": student_name,
            "time": press_time
        })
        
        # เรียงลำดับตามเวลา (ถ้าเวลาเท่ากัน Python จะสุ่ม/คงลำดับเดิม)
        game_state["results"].sort(key=lambda x: x["time"])
        
        # ส่งผลลัพธ์อัปเดตไปที่หน้าอาจารย์
        emit('update_leaderboard', game_state["results"], broadcast=True)

# อาจารย์สั่งรีเซต
@socketio.on('reset_game')
def handle_reset():
    game_state["is_active"] = False
    game_state["results"] = []
    emit('reset_game', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)

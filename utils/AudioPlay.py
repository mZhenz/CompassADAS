from pyaudio import PyAudio
import wave


def AudioPlay(audio_file):
    chunk = 1024  # 2014kb
    wf = wave.open(audio_file, 'rb')
    p = PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(),
                    rate=wf.getframerate(), output=True)

    # data = wf.readframes(chunk)  # 读取数据

    while True:
        # print(data)
        data = wf.readframes(chunk)
        if data == b'':
            break
        stream.write(data)
    stream.stop_stream()  # 停止数据流
    stream.close()
    p.terminate()  # 关闭 PyAudio
    # print('play函数结束！')


if __name__ == '__main__':
    audio_file = '../materials/music/4950.wav'  # 指定录音文件
    AudioPlay(audio_file)

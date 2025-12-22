import pygame
import os
import json
from typing import List

class MusicPlayer:
    def __init__(self):
        # 初始化pygame的音频模块
        pygame.mixer.init()
        
        # 播放器状态管理
        self.playlist: List[str] = []  # 播放列表
        self.current_song_index: int = -1  # 当前播放曲目索引
        self.is_playing: bool = False  # 是否正在播放

    # TODO: 根据主要情绪加载不同的播放列表
    def load_playlist(self, folder_path: str) -> None:
        """
        加载指定文件夹下的音频文件到播放列表
        支持格式：mp3, wav, ogg, flac
        """
        supported_formats = ('.mp3', '.wav', '.ogg', '.flac')
        self.playlist.clear()
        
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            print(f"[ERROR] {folder_path} Doesn't exist！")
            return
        
        # 遍历文件夹，收集音频文件
        for file in os.listdir(folder_path):
            if file.lower().endswith(supported_formats):
                self.playlist.append(os.path.join(folder_path, file))
        
        if not self.playlist:
            print("[WARNING] Can't find any music files in the folder！")
        else:
            print(f"[INFO] Succsessfully loaded {len(self.playlist)} music files")

    def load_playlist_by_emotion(self, results_json_path: str, music_base_path: str = "./resources/music") -> None:
        """
        从emotion结果JSON文件读取most_frequent_emotion字段，
        并根据该情绪加载对应的音乐播放列表
        
        Args:
            results_json_path: stream_results.json文件的路径
            music_base_path: 音乐文件夹的基础路径
        """
        try:
            with open(results_json_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            emotion = results.get('most_frequent_emotion')
            if not emotion:
                print("[ERROR] Can't found most_frequent_emotion!")
                return
            
            # 构建音乐文件夹路径
            emotion_music_path = os.path.join(music_base_path, emotion)
            
            # 加载该情绪对应的播放列表
            self.load_playlist(emotion_music_path)
            
        except FileNotFoundError:
            print(f"[ERROR] Can't Found {results_json_path}！")
        except json.JSONDecodeError:
            print(f"[Error] {results_json_path} is invalid!")
        except Exception as e:
            print(f"[ERROR] {e}")

    def play_song(self, index: int = None) -> None:
        """
        播放指定索引的曲目，若无索引则播放当前/第一首
        """
        # 处理播放列表为空的情况
        if not self.playlist:
            print("[ERROR] playlist is empty！")
            return
        
        # 确定要播放的曲目索引
        if index is not None:
            if 0 <= index < len(self.playlist):
                self.current_song_index = index
            else:
                print(f"[ERROR] {index} is out of range！")
                return
        elif self.current_song_index == -1:
            # 首次播放，默认播放第一首
            self.current_song_index = 0
        
        # 停止当前播放的音频（如果有）
        pygame.mixer.music.stop()
        
        # 加载并播放指定曲目
        song_path = self.playlist[self.current_song_index]
        try:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            self.is_playing = True
            print(f"正在播放：{os.path.basename(song_path)}")
        except Exception as e:
            print(f"播放失败：{e}")
            self.is_playing = False

    def pause_song(self) -> None:
        """暂停当前播放的曲目"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            print("已暂停播放")

    def resume_song(self) -> None:
        """恢复暂停的曲目"""
        if not self.is_playing and self.current_song_index != -1:
            pygame.mixer.music.unpause()
            self.is_playing = True
            print("恢复播放")

    def stop_song(self) -> None:
        """停止当前播放的曲目"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.current_song_index = -1
        print("已停止播放")

    def next_song(self) -> None:
        """播放下一首曲目（循环）"""
        if not self.playlist:
            print("错误：播放列表为空！")
            return
        
        # 计算下一首索引（循环播放）
        self.current_song_index = (self.current_song_index + 1) % len(self.playlist)
        self.play_song(self.current_song_index)

    def prev_song(self) -> None:
        """播放上一首曲目（循环）"""
        if not self.playlist:
            print("错误：播放列表为空！")
            return
        
        # 计算上一首索引（循环播放）
        self.current_song_index = (self.current_song_index - 1) % len(self.playlist)
        self.play_song(self.current_song_index)

# 测试播放器
if __name__ == "__main__":
    current_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_path)
    parent_dir = os.path.dirname(current_dir)

    # 创建播放器实例
    player = MusicPlayer()
    
    results_json_path = parent_dir+"/results/emotion/stream_results.json"
    music_base_path = parent_dir+"/resources/music"
    player.load_playlist_by_emotion(results_json_path, music_base_path)
    
    # 简单的交互演示
    print("\n=== 音乐播放器操作说明 ===")
    print("1. 播放")
    print("2. 暂停")
    print("3. 恢复")
    print("4. 下一首")
    print("5. 上一首")
    print("6. 停止")
    print("7. 退出")
    print("==========================\n")
    
    while True:
        command = int(input("请输入操作序号：").strip())
        if command == 1:
            player.play_song()
        elif command == 2:
            player.pause_song()
        elif command == 3:
            player.resume_song()
        elif command == 4:
            player.next_song()
        elif command == 5:
            player.prev_song()
        elif command == 6:
            player.stop_song()
        elif command == 7:
            player.stop_song()
            print("退出播放器")
            break
        else:
            print("无效命令，请重新输入！")
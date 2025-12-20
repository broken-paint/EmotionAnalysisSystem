# 推理结果协议

`results\emotion`的使用方法及各字段说明

请使用 `emotion` 字段作为识别结果

::: warning
JSON 文件是不支持注释的，文本中的注释仅用于演示，请勿直接复制使用
:::

## 完整字段一览

```json
{
    "source": "rtsp://username:password@address:554/*",     // rstp地址（或视频路径，webcam id）
    "timestamp": "YYYY-MM-DDThh:mm:ss",                     // 时间戳，下同
    "frames": [                                             // 不同帧的详细数据
        {
            "frame_index": 30,                              // 帧索引，下标从0开始
            "timestamp": "YYYY-MM-DDThh:mm:ss",             
            "faces": [                                      // 识别到的面部，可能有多个
                {
                    "id": 0,                                // 当前帧的第几个面部，下标从0开始
                    "bbox": {                               // 位置
                        "x": 1170,
                        "y": 326,
                        "width": 1022,
                        "height": 1022
                    },
                    "emotion": "neutral",                   // 结果
                    "confidence": 0.6330487132072449,       // 置信度
                    "scores": {                             // 各个表情的得分
                        "angry": 0.021171674132347107,
                        "disgust": 0.0010418386664241552,
                        "fear": 0.07495257258415222,
                        "happy": 0.02079041302204132,
                        "neutral": 0.6330487132072449,
                        "sad": 0.23896072804927826,
                        "surprise": 0.010034057311713696
                    }
                }
            ]
        }
    ]
}
```
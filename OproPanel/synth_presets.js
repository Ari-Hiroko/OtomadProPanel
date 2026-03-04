window.SynthPresets = {
    // 默认主音：12.5% 占空比的 FC/NES 经典脉冲波
    "lead": { wave: "pulse", duty: 0.125, attack: 0.01, decay: 0.15, sustain: 0.3, release: 0.1 },
    // 贝斯：标准的三角波，稍微长一点的释放时间
    "bass": { wave: "triangle", duty: 0.5, attack: 0.05, decay: 0.2, sustain: 0.8, release: 0.15 },
    // 铺底和弦：正弦波，长起音和长释放
    "pad": { wave: "sine", duty: 0.5, attack: 0.4, decay: 0.3, sustain: 0.6, release: 0.6 },
    // 鼓/打击乐：使用白噪声模拟（wave 设为 noise 即可）
    "drum": { wave: "noise", duty: 0.5, attack: 0.001, decay: 0.1, sustain: 0.0, release: 0.05 }
};
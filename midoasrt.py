import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage

def create_song(filename="sinoka_track.mid", bpm=92):
    mid = MidiFile(ticks_per_beat=480)
    tempo = mido.bpm2tempo(bpm)

    # --- 트랙 1: 코드 패드 / EP (Ch 0) ---
    chord_track = MidiTrack()
    mid.tracks.append(chord_track)
    chord_track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
    # 4: Electric Piano 1 (General MIDI 기준)
    chord_track.append(Message('program_change', channel=0, program=4, time=0))

    # Fmaj7 -> Em7 -> Am7 -> Gm7 - C7 (8마디 루프 x 2 = 16마디)
    chords = [
        # (음정 리스트, 길이 in beats)
        ([53, 57, 60, 64], 4),      # Fmaj7
        ([52, 55, 59, 62], 4),      # Em7
        ([57, 60, 64, 67], 4),      # Am7
        ([55, 58, 62, 65], 2),      # Gm7
        ([48, 55, 58, 64], 2),      # C7 (9)
    ] * 4  # 16마디 구성

    ticks_per_beat = mid.ticks_per_beat

    for notes, beats in chords:
        duration = int(beats * ticks_per_beat)
        # 코드 온 (약간 아르페지오 느낌 나게 미세 딜레이)
        for i, note in enumerate(notes):
            chord_track.append(Message('note_on', channel=0, note=note, velocity=68, time=(15 if i > 0 else 0)))
        
        # 첫 음 오프 시 전체 길이에서 앞선 딜레이만큼 차감
        total_delay = 15 * (len(notes) - 1)
        chord_track.append(Message('note_off', channel=0, note=notes[0], velocity=0, time=duration - total_delay))
        for note in notes[1:]:
            chord_track.append(Message('note_off', channel=0, note=note, velocity=0, time=0))

    # --- 트랙 2: 리드 멜로디 (Ch 1) ---
    melody_track = MidiTrack()
    mid.tracks.append(melody_track)
    # 81: Lead 2 (sawtooth) 또는 11: Vibraphone
    melody_track.append(Message('program_change', channel=1, program=11, time=0))

    # (음정, 길이 in beats, 벨로시티) -> 음정이 None이면 쉼표
    phrase_a = [
        (None, 1.0, 0),
        (76, 0.5, 85), (79, 0.5, 90), (81, 1.5, 95), (79, 0.5, 80), # Bar 1 (Fmaj7)
        (76, 1.0, 88), (74, 0.5, 82), (72, 1.5, 85), (74, 1.0, 80), # Bar 2 (Em7)
        (76, 1.5, 92), (79, 0.5, 86), (72, 2.0, 84),                # Bar 3 (Am7)
        (74, 1.0, 85), (72, 0.5, 80), (70, 1.5, 88), (67, 1.0, 78), # Bar 4 (Gm7-C7)
    ]

    phrase_b = [
        (69, 1.0, 88), (72, 0.5, 84), (76, 1.5, 94), (79, 1.0, 90), # Bar 5
        (81, 1.5, 98), (79, 0.5, 88), (76, 1.0, 85), (74, 1.0, 82), # Bar 6
        (72, 2.0, 90), (74, 0.5, 84), (76, 0.5, 88), (79, 1.0, 92), # Bar 7
        (76, 3.0, 95), (None, 1.0, 0),                              # Bar 8
    ]

    melody = (phrase_a + phrase_b) * 2
    rest_buffer = 0

    for note, beats, vel in melody:
        duration = int(beats * ticks_per_beat)
        if note is None:
            rest_buffer += duration
        else:
            melody_track.append(Message('note_on', channel=1, note=note, velocity=vel, time=rest_buffer))
            melody_track.append(Message('note_off', channel=1, note=note, velocity=0, time=duration))
            rest_buffer = 0

    # --- 트랙 3: 베이스 라인 (Ch 2) ---
    bass_track = MidiTrack()
    mid.tracks.append(bass_track)
    # 33: Electric Bass (finger)
    bass_track.append(Message('program_change', channel=2, program=33, time=0))

    bass_pattern = [
        # Bar 1: F
        (41, 1.5, 95), (41, 0.5, 75), (48, 1.0, 85), (45, 1.0, 80),
        # Bar 2: E
        (40, 1.5, 95), (40, 0.5, 75), (47, 1.0, 85), (43, 1.0, 80),
        # Bar 3: A
        (45, 1.5, 95), (45, 0.5, 75), (52, 1.0, 85), (48, 1.0, 80),
        # Bar 4: G -> C
        (43, 1.5, 95), (43, 0.5, 75), (36, 1.5, 95), (43, 0.5, 80),
    ] * 4

    for note, beats, vel in bass_pattern:
        duration = int(beats * ticks_per_beat)
        # 스타카토 느낌을 위해 길이를 90%만 유지하고 10%는 여백으로 둠
        play_len = int(duration * 0.9)
        gap_len = duration - play_len
        bass_track.append(Message('note_on', channel=2, note=note, velocity=vel, time=0))
        bass_track.append(Message('note_off', channel=2, note=note, velocity=0, time=play_len))
        if gap_len > 0:
            # 다음 노트 대기용 더미 오프 대신 다음 note_on의 time으로 처리하기 위해
            # 간단히 음 길이를 꽉 채우거나 쉬게 조정 가능. 여기선 깔끔하게 꽉 채움:
            pass

    # 위 베이스 루프에서 gap_len을 정확히 반영하도록 재작성된 깔끔한 루프:
    bass_track.clear()
    bass_track.append(Message('program_change', channel=2, program=33, time=0))
    rest_buf = 0
    for note, beats, vel in bass_pattern:
        duration = int(beats * ticks_per_beat)
        play_len = int(duration * 0.88)
        bass_track.append(Message('note_on', channel=2, note=note, velocity=vel, time=rest_buf))
        bass_track.append(Message('note_off', channel=2, note=note, velocity=0, time=play_len))
        rest_buf = duration - play_len

    mid.save(filename)
    print(f"'{filename}' 생성 완료! (BPM: {bpm}, 총 3트랙)")

if __name__ == "__main__":
    create_song()

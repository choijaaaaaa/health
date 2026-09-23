# 다시 뽑아야 할 클립 (2026-09-24, 색인 작업 중 발견)

프레임을 하나씩 보다 나온 것들. **쓸 수 없거나 이름과 너무 달라 혼선만 준다.**

| 클립 | 문제 | 대신 필요한 것 |
|---|---|---|
| `act_sniff_self` | 6초 내내 몸을 조금 트는 것뿐 — 냄새 맡는 동작도 점등도 없다 | 어깨·옷깃에 코를 대고 들이마시는 동작 + 코·비강 점등(체취·구취 카테고리가 통째로 막혀 있다) |
| `act_rub_nose` | 점등이 없고 후반부에 인체 모델이 남성형→여성형으로 바뀌어 장면이 끊긴다 | 콧등·콧방울을 손등으로 밀어 올리는 동작 + 비강 점등 |

## 참고 — 못 쓰는 건 아니지만 제약이 있는 것

- **점등이 아예 없는 기전**: `m_electrolyte_imbalance` · `m_fibrosis` · `m_layer_separation` ·
  `m_muscle_wasting` · `m_tissue_laxity` · `m_vision_field_loss` · `m_pressure_imbalance` ·
  `m_motility_speedup` · `m_vitreous_floaters`. 호박색으로 부위가 켜지는 연출이 필요한 자리엔 못 쓴다.
- **강조색이 캐논과 다른 것**: `m_cartilage_wear`(분홍) · `m_sensory_decline`(흰-청색).
- **부위인데 전체가 켜지는 것**: `part_bladder`(하반신 전체) · `part_spine_lumbar`(전신) ·
  `part_mouth_teeth`(두개골 전체) · `part_skin`(블록 전체). `scripts/make_part_clip.py --region`으로
  다시 만들 수 있다(좌표 예시는 CLIP_NOTES.md).

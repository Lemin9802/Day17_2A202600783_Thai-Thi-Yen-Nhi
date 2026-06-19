# Reflection — Day 17 (≤ 200 words)

Answer briefly, in your own words. This is graded on reasoning, not length.

1. **The flywheel.** Day 13 emitted agent traces; today you turned them into an
   eval set and DPO pairs that Day 22 will train on. Which step in
   `traces → Bronze → datasets` would break most silently in production if you
   got it wrong — and how would you detect it?

   The most silent failure is flattening nested spans into Bronze incorrectly, especially losing `trace_id`, `parent_id`, `outcome`, or `split`. The pipeline may still run, but the eval set and DPO pairs become wrong. I would detect it with schema checks, span-count reconciliation per trace, and comparing `trace_summary` against the raw traces.

2. **Decontamination.** Your run dropped 2 of 3 preference pairs because their
   prompts were in the eval set. What concretely goes wrong if you *skip* this
   step and train on those pairs? How would the lie show up in your metrics?

   If I skip decontamination, the model trains on eval prompts and can memorize the “test questions.” Offline metrics such as eval accuracy or win rate would look artificially high, while production performance on unseen prompts would not improve.

3. **Point-in-time.** The naive join leaked a future `lifetime_spend` into the
   training row. Describe one feature in a system you know that would be
   dangerous to join without an `ASOF`/point-in-time guard.

   In an e-commerce or churn system, `lifetime_spend` is dangerous without an `ASOF` guard. A training row from June 1 could accidentally use spend from June 4, causing future leakage and training-serving skew.

4. **Graph vs vector.** From `kg_demo.py`, name one question the knowledge graph
   answers well that flat chunk retrieval (`embed.py`) would struggle with, and
   one where the graph is overkill.

   The graph answers “Where does a widget ship from?” well by traversing `widget → accessory → Hanoi fulfillment center`. It is overkill for a simple one-hop question like “Are widgets returnable?”
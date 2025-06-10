  - task: "Time Decay in Ensemble Predictions"
    implemented: true
    working: true
    file: "/app/frontend/src/components/EnsemblePredictions.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "testing"
        comment: "Testing the time decay controls in the Ensemble Predictions tab."
      - working: true
        agent: "testing"
        comment: "Successfully verified that time decay controls have been added to the Ensemble Predictions tab. The tab includes a dedicated 'Time Decay Weighting' section with an enable/disable checkbox that is enabled by default. The section also includes a 'Decay Preset' dropdown with multiple options including aggressive (2-month half-life), moderate (4-month half-life), conservative (8-month half-life), linear (10% decay per month), and none (no time decay). The time decay controls are fully functional - when the checkbox is unchecked, the decay preset dropdown is properly disabled, and when checked, it's enabled. The time decay settings are properly passed to the backend API when making predictions, as seen in the request parameters. This implementation allows users to control how historical match data is weighted in ensemble predictions, with more recent matches having higher impact than older ones based on the selected decay preset."
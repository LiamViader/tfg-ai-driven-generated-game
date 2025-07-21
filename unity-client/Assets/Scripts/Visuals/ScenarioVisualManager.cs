using UnityEngine;
using System.Collections.Generic;
using System.Collections;
public class ScenarioVisualManager : MonoBehaviour
{
    public static ScenarioVisualManager Instance;

    [SerializeField]
    private GameObject scenarioPrefab;
    [SerializeField]
    private Transform scenarioParent;
    [SerializeField]
    private int loadRadius = 2;

    private string _currentScenarioId = null;

    private readonly Dictionary<string, GameObject> _activeScenarios = new();

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    public void SetFocusScenario(string newScenarioId, System.Action onScenarioChangeVisually = null)
    {
        if (_currentScenarioId == newScenarioId) return;

        string prevScenarioId = _currentScenarioId;
        _currentScenarioId = newScenarioId;

        // This logic should be called while the screen is faded out.
        RefreshVisualScenarios(newScenarioId);
        FocusCameraOn(newScenarioId);
        TransitionBetweenScenariosImmediately(prevScenarioId, newScenarioId, onScenarioChangeVisually);
    }

    private void TransitionBetweenScenariosImmediately(string fromId, string toId, System.Action onScenarioChangeVisually = null)
    {
        if (fromId != null && _activeScenarios.TryGetValue(fromId, out var fromGoImmediate))
        {
            fromGoImmediate.SetActive(false);
            SetCanvasGroupInteraction(fromGoImmediate, false, false);
        }

        if (_activeScenarios.TryGetValue(toId, out var toGoImmediate))
        {
            toGoImmediate.SetActive(true);
            var toFader = GetFader(toId);
            if (toFader != null) toFader.SetAlpha(1f);
            SetCanvasGroupInteraction(toGoImmediate, true, true);
        }

        onScenarioChangeVisually?.Invoke();
    }

    /// </summary>
    public IEnumerator FadeOutCurrentScenario(float duration = 0.5f, System.Action onScenarioFadeOut = null)
    {
        if (string.IsNullOrEmpty(_currentScenarioId))
        {
            yield break; // Exit if there's no current scenario
        }
        string current_scenario_id = _currentScenarioId;
        var fromFader = GetFader(current_scenario_id);
        if (fromFader != null)
        {
            Debug.Log($"Fading out scenario: {_currentScenarioId}");
            if (_activeScenarios.TryGetValue(current_scenario_id, out var fromGoStart))
            {
                SetCanvasGroupInteraction(fromGoStart, false, false);
                fromGoStart.gameObject.SetActive(true);
            }
            // We call and wait for the Fader's own coroutine to complete.
            yield return fromFader.FadeTo(0f, duration);
            if (_activeScenarios.TryGetValue(current_scenario_id, out var fromGoStarted))
            {
                fromGoStarted.gameObject.SetActive(false);
            }

            onScenarioFadeOut?.Invoke();
        }
    }

    public IEnumerator FadeInScenario(string scenarioId, float duration = 0.5f, System.Action onScenarioFadeIn = null)
    {
        if (string.IsNullOrEmpty(scenarioId))
        {
            yield break;
        }

        var toFader = GetFader(scenarioId);
        if (toFader != null)
        {
            if (_activeScenarios.TryGetValue(scenarioId, out var toGoEnd))
            {
                toGoEnd.gameObject.SetActive(true);
            }
            Debug.Log($"Fading in scenario: {scenarioId}");
            // Make sure the object is active and transparent before fading in

            toFader.SetAlpha(0f);
            // We call and wait for the Fader's own coroutine to complete.
            yield return toFader.FadeTo(1f, duration);
            if (_activeScenarios.TryGetValue(scenarioId, out var toGoFinish))
            {
                SetCanvasGroupInteraction(toGoFinish, true, true);
            }
            onScenarioFadeIn?.Invoke();
        }
    }


    private void FocusCameraOn(string scenarioId)
    {
        if (_activeScenarios.TryGetValue(scenarioId, out var go))
        {

            Camera.main.transform.position = new Vector3(
                go.transform.position.x,
                go.transform.position.y,
                Camera.main.transform.position.z
            );
        }
    }


    public void RefreshVisualScenarios(string centerScenarioId)
    {
        var toKeep = GameManager.Instance.GetScenariosInRadius(centerScenarioId, loadRadius);

        foreach (var id in toKeep)
        {

            if (!_activeScenarios.ContainsKey(id))
            {
                var data = GameManager.Instance.GetScenario(id);
                if (data == null) continue;

                var go = Instantiate(scenarioPrefab, scenarioParent);
                SetupScenarioVisual(go, data);
                _activeScenarios[id] = go;
            }
            else
            {
                var data = GameManager.Instance.GetScenario(id);
                if (data == null) continue;
                if (_activeScenarios.TryGetValue(id, out var go2)){
                    go2.SetActive(true);
                    UpdateScenarioVisual(go2, data);
                }
                

            }

            _activeScenarios[id].SetActive(false);
        }

        if (_currentScenarioId!=null && _activeScenarios.TryGetValue(_currentScenarioId, out var scenarioCurrent))
        {
            scenarioCurrent.SetActive(true);
        }

        var toRemove = new List<string>();
        foreach (var kvp in _activeScenarios)
        {
            if (!toKeep.Contains(kvp.Key))
            {
                Destroy(kvp.Value);
                toRemove.Add(kvp.Key);
            }
        }

        foreach (var id in toRemove)
            _activeScenarios.Remove(id);
    }

    private void SetupScenarioVisual(GameObject go, ScenarioData data)
    {
        var view = go.GetComponent<ScenarioView>() ?? go.AddComponent<ScenarioView>();
        view.Initialize(data);
        view.SpawnCharacters(data.characterIds);
        var cg = go.GetComponent<CanvasGroup>();
        if (cg == null)
        {
            cg = go.AddComponent<CanvasGroup>();
        }
        cg.interactable = false;
        cg.blocksRaycasts = false;
    }

    private void UpdateScenarioVisual(GameObject go, ScenarioData data)
    {
        var view = go.GetComponent<ScenarioView>() ?? go.AddComponent<ScenarioView>();
        view.Initialize(data);
        view.SpawnCharacters(data.characterIds);
        var cg = go.GetComponent<CanvasGroup>();
        if (cg == null)
        {
            cg = go.AddComponent<CanvasGroup>();
        }
        cg.interactable = false;
        cg.blocksRaycasts = false;
    }

    private ScenarioFader GetFader(string scenarioId)
    {
        if (scenarioId == null) return null;
        if (!_activeScenarios.TryGetValue(scenarioId, out var go)) return null;
        return go.GetComponent<ScenarioFader>();
    }


    private void SetCanvasGroupInteraction(GameObject scenarioGo, bool interactable, bool blocksRaycasts)
    {
        if (scenarioGo == null) return;

        var cg = scenarioGo.GetComponent<CanvasGroup>();
        if (cg == null)
        {
            cg = scenarioGo.AddComponent<CanvasGroup>();
        }
        cg.interactable = interactable;
        cg.blocksRaycasts = blocksRaycasts;
    }
}
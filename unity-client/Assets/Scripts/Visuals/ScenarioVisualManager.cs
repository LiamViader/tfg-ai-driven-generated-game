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

    public void SetFocusScenario(string newScenarioId)
    {

        if (_currentScenarioId == newScenarioId)
            return;

        string prevScenarioId = _currentScenarioId;
        _currentScenarioId = newScenarioId;

        RefreshVisualScenarios(newScenarioId);

        FocusCameraOn(newScenarioId);

        StartCoroutine(TransitionBetweenScenarios(prevScenarioId, newScenarioId));
    }


    private IEnumerator TransitionBetweenScenarios(string fromId, string toId)
    {
        float duration = 0.5f;

        CanvasGroup fromGroup = GetCanvasGroup(fromId);
        CanvasGroup toGroup = GetCanvasGroup(toId);

        if (toGroup != null) toGroup.alpha = 0f;

        float t = 0f;
        while (t < duration)
        {
            t += Time.deltaTime;
            float progress = t / duration;

            if (fromGroup != null)
                fromGroup.alpha = Mathf.Lerp(1f, 0f, progress);

            if (toGroup != null)
                toGroup.alpha = Mathf.Lerp(0f, 1f, progress);

            yield return null;
        }

        if (fromGroup != null)
        {
            fromGroup.alpha = 0f;
            fromGroup.interactable = false;
            fromGroup.blocksRaycasts = false;
        }

        if (toGroup != null)
        {
            toGroup.alpha = 1f;
            toGroup.interactable = true;
            toGroup.blocksRaycasts = true;
        }

        foreach (var kvp in _activeScenarios)
        {
            bool isCurrent = kvp.Key == toId;
            kvp.Value.SetActive(isCurrent);
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

            _activeScenarios[id].SetActive(true);
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

        var cg = go.GetComponent<CanvasGroup>();
        if (cg == null)
        {
            cg = go.AddComponent<CanvasGroup>();
        }
        cg.interactable = false;
        cg.blocksRaycasts = false;
    }
    private CanvasGroup GetCanvasGroup(string scenarioId)
    {
        if (scenarioId == null) return null;
        if (!_activeScenarios.TryGetValue(scenarioId, out var go)) return null;
        return go.GetComponent<CanvasGroup>();
    }
}
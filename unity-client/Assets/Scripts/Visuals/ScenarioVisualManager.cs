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

    public void SetFocusScenario(string newScenarioId, bool immediately, System.Action onScenarioChangeVisually = null)
    {

        if (_currentScenarioId == newScenarioId)
            return;

        string prevScenarioId = _currentScenarioId;
        _currentScenarioId = newScenarioId;

        RefreshVisualScenarios(newScenarioId);

        FocusCameraOn(newScenarioId);
        if (immediately)
        {
            TransitionBetweenScenariosImmediately(prevScenarioId, newScenarioId, onScenarioChangeVisually);
        }
        else
        {
            StartCoroutine(TransitionBetweenScenarios2(prevScenarioId, newScenarioId, onScenarioChangeVisually));
        }



    }

    private void TransitionBetweenScenariosImmediately(string fromId, string toId, System.Action onScenarioChangeVisually = null)
    {

        foreach (var kvp in _activeScenarios)
        {
            bool isCurrent = kvp.Key == toId;
            kvp.Value.SetActive(isCurrent);
        }

    }

    private IEnumerator TransitionBetweenScenarios1(string fromId, string toId, System.Action onScenarioChangeVisually = null)
    {
        float duration = 0.5f;

        var fromFader = GetFader(fromId);
        var toFader = GetFader(toId);

        if (toFader != null)
            toFader.SetAlpha(0f);

        if (_activeScenarios.TryGetValue(toId, out var toGo))
            toGo.SetActive(true);

        if (_activeScenarios.TryGetValue(fromId, out var fromGo))
            fromGo.SetActive(true);

        bool done = false;

        if (fromFader != null)
            fromFader.FadeTo(0f, duration);

        if (toFader != null)
            yield return toFader.FadeTo(1f, duration, () => done = true);

        while (!done)
            yield return null;

        

        foreach (var kvp in _activeScenarios)
            kvp.Value.SetActive(kvp.Key == toId);

        onScenarioChangeVisually?.Invoke();
    }

    private IEnumerator TransitionBetweenScenarios2(string fromId, string toId, System.Action onScenarioChangeVisually = null)
    {
        float duration = 1f;

        var fromFader = GetFader(fromId);
        var toFader = GetFader(toId);

        // Activar el nuevo escenario (pero mantenerlo invisible)
        if (_activeScenarios.TryGetValue(toId, out var toGo))
            toGo.SetActive(true);

        if (_activeScenarios.TryGetValue(fromId, out var fromGo))
            fromGo.SetActive(true);

        if (toFader != null)
            toFader.SetAlpha(0f); // invisible antes de empezar

        // Fade out del escenario anterior
        if (fromFader != null)
        {
            bool doneFrom = false;
            yield return fromFader.FadeTo(0f, duration*2, () => doneFrom = true);
            while (!doneFrom) yield return null;
        }

        // Desactivar el escenario anterior
        if (_activeScenarios.TryGetValue(fromId, out var fromGo2))
            fromGo2.SetActive(false);

        onScenarioChangeVisually?.Invoke();

        // Fade in del nuevo escenario
        if (toFader != null)
        {
            bool doneTo = false;
            yield return toFader.FadeTo(1f, duration, () => doneTo = true);
            while (!doneTo) yield return null;
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

            _activeScenarios[id].SetActive(false);
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
    private ScenarioFader GetFader(string scenarioId)
    {
        if (scenarioId == null) return null;
        if (!_activeScenarios.TryGetValue(scenarioId, out var go)) return null;
        return go.GetComponent<ScenarioFader>();
    }

}
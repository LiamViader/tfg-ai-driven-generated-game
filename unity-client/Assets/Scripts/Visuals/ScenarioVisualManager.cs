using UnityEngine;
using System.Collections.Generic;
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
        if (Instance == null) Instance = this;
        else Destroy(gameObject);
    }

    public void SetFocusScenario(string scenarioId)
    {

        RefreshVisualScenarios(scenarioId);

        FocusCameraOn(scenarioId);

        // 4. (Opcional) Transición visual: fade, desplazamiento, etc.
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
    }
}
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using System.Linq;
using System.Globalization;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance;

    private readonly Dictionary<string, ScenarioData> _scenarios = new();
    private readonly Dictionary<string, CharacterData> _characters = new();
    private readonly Dictionary<string, ConnectionData> _connections = new();
    private readonly Dictionary<string, Dictionary<string, CharacterOptionEventData>> _characterContextualOptions = new();

    public string CurrentScenarioId { get; private set; }
    public string PlayerCharacterId { get; private set; }

    private string _lastCheckpointId;
    public string LastCheckpointId => _lastCheckpointId;

    [SerializeField] private List<AssignCameraToCanvas> _assignCameraToCanvas;

    public void SetCheckpointId(string checkpointId)
    {
        _lastCheckpointId = checkpointId;
    }

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else Destroy(gameObject);
    }


    // Accessors
    public ScenarioData GetScenario(string id) => _scenarios.TryGetValue(id, out var s) ? s : null;
    public CharacterData GetCharacter(string id) => _characters.TryGetValue(id, out var c) ? c : null;
    public ConnectionData GetConnection(string id) => _connections.TryGetValue(id, out var c) ? c : null;

    public List<CharacterOptionEventData> GetCharacterContextualOptions(string characterId)
    {
        if (_characterContextualOptions.TryGetValue(characterId, out var optionsDict))
        {
            // Devuelve una lista de los valores del diccionario interno
            return optionsDict.Values.ToList();
        }
        return new List<CharacterOptionEventData>();
    }
    public CharacterOptionEventData GetCharacterContextualOption(string characterId, string condition_id)
    {
        if (_characterContextualOptions.TryGetValue(characterId, out var optionsDict))
        {
            if (optionsDict.TryGetValue(condition_id, out var data))
            {
                // Devuelve una lista de los valores del diccionario interno
                return data;
            }
        }
        return null;
    }

    public IEnumerable<ScenarioData> GetAllScenarios() => _scenarios.Values;
    public IEnumerable<ConnectionData> GetAllConnections() => _connections.Values;

    public void SetCurrentScenario(string id) => CurrentScenarioId = id;
    public void SetPlayerCharacterId(string id) {
        PlayerCharacterId = id;
        CharacterData player = GetCharacter(id);
        if (player != null)
        {
            UIManager.Instance.SetPlayerData(player);
        }
    }

    // Controlled mutation
    public void AddOrUpdateScenario(ScenarioData scenario) => _scenarios[scenario.id] = scenario;
    public void RemoveScenario(string id) => _scenarios.Remove(id);

    public void AddOrUpdateCharacter(CharacterData character) {
        _characters[character.id] = character;
        if (character.id == PlayerCharacterId)
        {
            UIManager.Instance.SetPlayerData(character);
        }
    }
    public void RemoveCharacter(string id) => _characters.Remove(id);

    public void AddOrUpdateConnection(ConnectionData connection) => _connections[connection.connectionId] = connection;
    public void RemoveConnection(string id) => _connections.Remove(id);

    public void SetScenarioConnection(string scenarioId, string direction, string connectionId)
    {
        if (_scenarios.TryGetValue(scenarioId, out var scenario))
            scenario.connectionIdsByDirection[direction] = connectionId;
    }

    public void RemoveScenarioConnection(string connectionId)
    {
        foreach (var scenario in _scenarios.Values)
        {
            var toRemove = new List<string>();
            foreach (var kvp in scenario.connectionIdsByDirection)
            {
                if (kvp.Value == connectionId)
                    toRemove.Add(kvp.Key);
            }

            foreach (var dir in toRemove)
                scenario.connectionIdsByDirection.Remove(dir);
        }
    }

    public void AddCharacterToScenario(string scenarioId, string characterId)
    {
        if (_scenarios.TryGetValue(scenarioId, out var scenario) && !scenario.characterIds.Contains(characterId))
        {
            scenario.characterIds.Add(characterId);
        }
    }

    public void RemoveCharacterFromScenarios(string characterId)
    {
        foreach (var scenario in _scenarios.Values)
            scenario.characterIds.Remove(characterId);
    }

    public void AddOrUpdateCharacterContextualOption(string characterId, CharacterOptionEventData optionData, string conditionId)
    {
        if (!_characterContextualOptions.ContainsKey(characterId))
        {
            _characterContextualOptions[characterId] = new Dictionary<string, CharacterOptionEventData>();
        }
        _characterContextualOptions[characterId][conditionId] = optionData;

        UIManager.Instance.CharacterOptionsUpdated(characterId);
    }

    public void RemoveCharacterContextualOption(string characterId, string conditionId)
    {
        if (_characterContextualOptions.TryGetValue(characterId, out var optionsDict))
        {
            if (optionsDict.Remove(conditionId))
            {
                UIManager.Instance.CharacterOptionsUpdated(characterId);
            }
        }
    }


    public HashSet<string> GetScenariosInRadius(string fromId, int radius)
    {
        var visited = new HashSet<string>();
        var queue = new Queue<(string id, int depth)>();
        queue.Enqueue((fromId, 0));
        visited.Add(fromId);

        while (queue.Count > 0)
        {
            var (currentId, depth) = queue.Dequeue();
            if (depth >= radius) continue;

            var currentScenario = GetScenario(currentId);
            if (currentScenario == null) continue;

            foreach (var connId in currentScenario.connectionIdsByDirection.Values)
            {
                var conn = GetConnection(connId);
                if (conn == null) continue;

                var neighborId = conn.scenarioAId == currentId ? conn.scenarioBId : conn.scenarioAId;
                if (neighborId != null && !visited.Contains(neighborId))
                {
                    visited.Add(neighborId);
                    queue.Enqueue((neighborId, depth + 1));
                }
            }
        }

        return visited;
    }

    public void TravelTo(string scenarioId)
    {

        ScenarioData scenarioTo = GetScenario(scenarioId);
        
        if (scenarioTo != null)
        {
            CurrentScenarioId = scenarioId;
            ScenarioVisualManager.Instance.SetFocusScenario(CurrentScenarioId);
            UIManager.Instance.SetPlayerBackgroundImage(scenarioTo.backgroundImage);
            UIManager.Instance.SetScenarioData(scenarioTo);
        }
    }

    public void InitializeWorld()
    {
        StartCoroutine(InitializeWorldCoroutine());
    }

    private IEnumerator InitializeWorldCoroutine()
    {
        string targetScene = "GameScene";

        if (SceneManager.GetActiveScene().name != targetScene)
        {
            var loadOp = SceneManager.LoadSceneAsync(targetScene);

            while (!loadOp.isDone)
                yield return null;
        }

        var player = GetCharacter(PlayerCharacterId);
        if (player == null || string.IsNullOrEmpty(player.presentInScenario))
        {
            Debug.LogError("No se puede encontrar el personaje del jugador o su escenario.");
            yield break;
        }

        UIManager.Instance.SetPlayerImage(player.portrait);
        SetCurrentScenario(player.presentInScenario);
        foreach (var assign in _assignCameraToCanvas)
        {
            assign.Assign();
        }

        ScenarioVisualManager.Instance.SetFocusScenario(CurrentScenarioId);
        ScenarioData scenarioTo = GetScenario(CurrentScenarioId);
        if (scenarioTo != null)
        {
            UIManager.Instance.SetPlayerBackgroundImage(scenarioTo.backgroundImage);
            UIManager.Instance.SetScenarioData(scenarioTo);
        }
    }

    public void TriggerEvent(string eventId)
    {
        Debug.Log($"Triggering event: {eventId}");
    }
}



using System.Collections.Generic;
using UnityEngine;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance;

    private readonly Dictionary<string, ScenarioData> _scenarios = new();
    private readonly Dictionary<string, CharacterData> _characters = new();
    private readonly Dictionary<string, ConnectionData> _connections = new();
    private readonly Dictionary<string, GameObject> _activeScenarios = new();

    public string CurrentScenarioId { get; private set; }
    public string PlayerCharacterId { get; private set; }

    private string _lastCheckpointId;
    public string LastCheckpointId => _lastCheckpointId;

    public void SetCheckpointId(string checkpointId)
    {
        // TODO send delete last checkpoint to backend to free memory
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

    public IEnumerable<ScenarioData> GetAllScenarios() => _scenarios.Values;
    public IEnumerable<ConnectionData> GetAllConnections() => _connections.Values;

    public void SetCurrentScenario(string id) => CurrentScenarioId = id;
    public void SetPlayerCharacterId(string id) => PlayerCharacterId = id;

    // Controlled mutation
    public void AddOrUpdateScenario(ScenarioData scenario) => _scenarios[scenario.id] = scenario;
    public void RemoveScenario(string id) => _scenarios.Remove(id);

    public void AddOrUpdateCharacter(CharacterData character) => _characters[character.id] = character;
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
            scenario.characterIds.Add(characterId);
    }

    public void RemoveCharacterFromScenarios(string characterId)
    {
        foreach (var scenario in _scenarios.Values)
            scenario.characterIds.Remove(characterId);
    }

    // Optional: activeScenario management too (for GameObjects)
}



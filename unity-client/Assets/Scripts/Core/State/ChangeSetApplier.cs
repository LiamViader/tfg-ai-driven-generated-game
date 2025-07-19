using UnityEngine;
using Api.Models;
using System.Collections.Generic;


public class ChangeSetApplier
{
    public void Apply(ChangesetResponse changeSet)
    {
        if (changeSet == null) return;

        if (!string.IsNullOrEmpty(changeSet.checkpoint_id))
            GameManager.Instance.SetCheckpointId(changeSet.checkpoint_id);

        var changes = changeSet.changes;
        if (changes == null) return;

        if (changes.map != null)
        {
            if (changes.map.scenarios != null)
                ApplyScenarios(changes.map.scenarios);

            if (changes.map.connections != null)
                ApplyConnections(changes.map.connections);
        }

        if (changes.characters != null)
        {
            if (changes.characters.registry != null)
                ApplyCharacters(changes.characters.registry);

            if (!string.IsNullOrEmpty(changes.characters.player_character_id))
                GameManager.Instance.SetPlayerCharacterId(changes.characters.player_character_id);
        }

        if (changes.events != null && changes.events.character_interaction_options_delta != null)
        {
            ApplyGameEventCharacterOptions(changes.events.character_interaction_options_delta);
        }
    }

    void ApplyScenarios(List<ScenarioOperation> scenarioChanges)
    {
        foreach (var s in scenarioChanges)
        {
            if (s == null || string.IsNullOrEmpty(s.op) || string.IsNullOrEmpty(s.id))
                continue;

            switch (s.op)
            {
                case "add":
                    {
                        var scenario = new ScenarioData
                        {
                            id = s.id,
                            name = s.name ?? "",
                            description = s.summary_description ?? "",
                            visualDescription = s.visual_description ?? "",
                            narrativeContext = s.narrative_context ?? "",
                            type = s.type ?? "",
                            zone = s.zone ?? "",
                            // backgroundImage = ImageLoader.LoadFromPath(s.image_path),
                        };

                        if (s.connections != null)
                        {
                            foreach (var connChange in s.connections)
                            {
                                if (string.IsNullOrEmpty(connChange?.direction)) continue;

                                if (!string.IsNullOrEmpty(connChange.value))
                                    scenario.connectionIdsByDirection[connChange.direction] = connChange.value;
                            }
                        }

                        GameManager.Instance.AddOrUpdateScenario(scenario);

                        if (!string.IsNullOrEmpty(s.image_path))
                        {
                            ImageLoadTracker.Instance.TrackImageLoad(
                                AssetsAPI.GetImage(s.image_path, tex =>
                                {
                                    scenario.backgroundImage = tex;
                                })
                            );
                        }

                        break;
                    }

                case "update":
                    {
                        var scenario = GameManager.Instance.GetScenario(s.id);
                        if (scenario == null) continue;

                        if (s.name != null) scenario.name = s.name;
                        if (s.summary_description != null) scenario.description = s.summary_description;
                        if (s.visual_description != null) scenario.visualDescription = s.visual_description;
                        if (s.narrative_context != null) scenario.narrativeContext = s.narrative_context;
                        if (s.type != null) scenario.type = s.type;
                        if (s.zone != null) scenario.zone = s.zone;

                        if (s.connections != null)
                        {
                            foreach (var connChange in s.connections)
                            {
                                if (string.IsNullOrEmpty(connChange?.direction)) continue;

                                switch (connChange.op)
                                {
                                    case "add":
                                    case "update":
                                        if (!string.IsNullOrEmpty(connChange.value))
                                            scenario.connectionIdsByDirection[connChange.direction] = connChange.value;
                                        else
                                            scenario.connectionIdsByDirection.Remove(connChange.direction);
                                        break;

                                    case "remove":
                                        scenario.connectionIdsByDirection.Remove(connChange.direction);
                                        break;
                                }
                            }
                        }

                        if (!string.IsNullOrEmpty(s.image_path))
                        {
                            ImageLoadTracker.Instance.TrackImageLoad(
                                AssetsAPI.GetImage(s.image_path, tex =>
                                {
                                    scenario.backgroundImage = tex;
                                })
                            );
                        }

                        GameManager.Instance.AddOrUpdateScenario(scenario);
                        break;
                    }

                case "remove":
                    GameManager.Instance.RemoveScenario(s.id);
                    break;
            }
        }

    }

    void ApplyConnections(List<ConnectionOperation> connectionChanges)
    {
        foreach (var conn in connectionChanges)
        {
            if (conn == null || string.IsNullOrEmpty(conn.op) || string.IsNullOrEmpty(conn.id))
                continue;

            if (conn.op == "add")
            {
                if (string.IsNullOrEmpty(conn.id) ||
                    string.IsNullOrEmpty(conn.scenario_a_id) ||
                    string.IsNullOrEmpty(conn.scenario_b_id) ||
                    string.IsNullOrEmpty(conn.direction_from_a))
                    continue;

                var connData = new ConnectionData
                {
                    connectionId = conn.id,
                    scenarioAId = conn.scenario_a_id,
                    scenarioBId = conn.scenario_b_id,
                    directionFromA = conn.direction_from_a,
                    directionFromB = DirectionUtils.GetOpposite(conn.direction_from_a),
                    type = conn.connection_type ?? "",
                    travelDescription = conn.travel_description ?? "",
                    exitAppearanceDescription = conn.exit_appearance_description ?? "",
                    isBlocked = conn.is_blocked ?? false
                };

                GameManager.Instance.AddOrUpdateConnection(connData);

                GameManager.Instance.SetScenarioConnection(connData.scenarioAId, connData.directionFromA, connData.connectionId);
                GameManager.Instance.SetScenarioConnection(connData.scenarioBId, connData.directionFromB, connData.connectionId);
            }
            else if (conn.op == "update")
            {
                var existing = GameManager.Instance.GetConnection(conn.id);
                if (existing == null)
                    continue;

                // Update todos los campos que vengan
                if (conn.scenario_a_id != null) existing.scenarioAId = conn.scenario_a_id;
                if (conn.scenario_b_id != null) existing.scenarioBId = conn.scenario_b_id;
                if (conn.direction_from_a != null)
                {
                    existing.directionFromA = conn.direction_from_a;
                    existing.directionFromB = DirectionUtils.GetOpposite(conn.direction_from_a);
                }

                if (conn.connection_type != null) existing.type = conn.connection_type;
                if (conn.travel_description != null) existing.travelDescription = conn.travel_description;
                if (conn.exit_appearance_description != null) existing.exitAppearanceDescription = conn.exit_appearance_description;
                if (conn.is_blocked != null) existing.isBlocked = conn.is_blocked.Value;

                GameManager.Instance.AddOrUpdateConnection(existing);
            }
            else if (conn.op == "remove")
            {
                GameManager.Instance.RemoveConnection(conn.id);
                GameManager.Instance.RemoveScenarioConnection(conn.id);
            }
        }
    }

    void ApplyCharacters(List<CharacterOperation> characterChanges)
    {
        foreach (var ch in characterChanges)
        {
            if (ch == null || string.IsNullOrEmpty(ch.op) || string.IsNullOrEmpty(ch.id))
                continue;

            switch (ch.op)
            {
                case "add":
                    {
                        var charData = new CharacterData
                        {
                            id = ch.id,
                            fullName = ch.identity?.full_name ?? "",
                            alias = ch.identity?.alias ?? "",
                            presentInScenario = ch.present_in_scenario ?? ""
                        };

                        GameManager.Instance.AddOrUpdateCharacter(charData);
                        GameManager.Instance.AddCharacterToScenario(charData.presentInScenario, charData.id);

                        if (!string.IsNullOrEmpty(ch.image_path))
                        {
                            ImageLoadTracker.Instance.TrackImageLoad(
                                AssetsAPI.GetImage(ch.image_path, tex =>
                                {
                                    charData.portrait = tex;
                                })
                            );
                        }

                        break;
                    }

                case "update":
                    {
                        var existing = GameManager.Instance.GetCharacter(ch.id);
                        if (existing == null) continue;

                        if (ch.identity?.full_name != null) existing.fullName = ch.identity.full_name;
                        if (ch.identity?.alias != null) existing.alias = ch.identity.alias;
                        if (ch.present_in_scenario != null)
                        {
                            if (existing.presentInScenario != ch.present_in_scenario)
                            {
                                GameManager.Instance.RemoveCharacterFromScenarios(existing.id);
                                existing.presentInScenario = ch.present_in_scenario;
                                GameManager.Instance.AddCharacterToScenario(existing.presentInScenario, existing.id);
                            }
                        }

                        if (!string.IsNullOrEmpty(ch.image_path))
                        {
                            ImageLoadTracker.Instance.TrackImageLoad(
                                AssetsAPI.GetImage(ch.image_path, tex =>
                                {
                                    existing.portrait = tex;
                                })
                            );
                        }

                        GameManager.Instance.AddOrUpdateCharacter(existing);
                        break;
                    }

                case "remove":
                    {
                        GameManager.Instance.RemoveCharacter(ch.id);
                        GameManager.Instance.RemoveCharacterFromScenarios(ch.id);
                        break;
                    }
            }
        }
    }

    void ApplyGameEventCharacterOptions(Dictionary<string, List<GameEventCharacterOptionOperation>> characterOptionsDelta)
    {
        foreach (var entry in characterOptionsDelta)
        {
            string characterId = entry.Key;
            List<GameEventCharacterOptionOperation> operations = entry.Value;

            foreach (var op in operations)
            {
                if (op == null || string.IsNullOrEmpty(op.op) || string.IsNullOrEmpty(op.condition_id))
                {
                    Debug.LogWarning($"Skipping invalid character option operation: op='{op?.op}', condition_id='{op?.condition_id}'");
                    continue;
                }

                switch (op.op)
                {
                    case "add":
                        CharacterOptionEventData optionData = new CharacterOptionEventData {
                            conditionId = op.condition_id,
                            eventId = op.event_id ?? "",
                            title = op.title ?? "",
                            description = op.description ?? "",
                            menuLabel = op.menu_label ?? "",
                            isRepeatable = op.is_repeatable ?? false,
                        };

                        GameManager.Instance.AddOrUpdateCharacterContextualOption(characterId, optionData, op.condition_id);

                        break;
                    case "update":
                        var existing = GameManager.Instance.GetCharacterContextualOption(characterId, op.condition_id);
                        if (existing == null) continue;

                        if (op.event_id != null) existing.eventId = op.event_id;
                        if (op.title != null) existing.title = op.title;
                        if (op.description != null) existing.description = op.description;
                        if (op.menu_label != null) existing.menuLabel = op.menu_label;
                        if (op.is_repeatable != null) existing.isRepeatable = op.is_repeatable ?? false;

                        GameManager.Instance.AddOrUpdateCharacterContextualOption(characterId, existing, op.condition_id);
                        break;
                    case "remove":
                        GameManager.Instance.RemoveCharacterContextualOption(characterId, op.condition_id);
                        break;
                    default:
                        Debug.LogWarning($"Unknown operation type '{op.op}' for character option {op.condition_id}");
                        break;
                }
            }
        }
    }
}

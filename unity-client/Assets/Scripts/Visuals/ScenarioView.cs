using System.Collections.Generic;
using UnityEngine;

public class ScenarioView : MonoBehaviour
{
    [SerializeField]
    private SpriteRenderer _spriteRenderer;
    [SerializeField]
    private BoxCollider2D _characterSpawnArea;
    [SerializeField] private GameObject _characterPrefab;
    [SerializeField] private float _minCharacterScale = 0.65f;
    [SerializeField] private float _maxCharacterScale = 1f;
    [SerializeField] private float _minSpawnDistance = 3f;
    [SerializeField] private float _yWeight = 2f;

    private List<Vector2> _spawnedPositions = new();
    private readonly Dictionary<string, GameObject> _spawnedCharacters = new();

    public void Initialize(ScenarioData data)
    {
        if (data.backgroundImage != null)
        {
            Sprite sprite = Sprite.Create(
                data.backgroundImage,
                new Rect(0, 0, data.backgroundImage.width, data.backgroundImage.height),
                new Vector2(0.5f, 0.5f), 
                100f                    
            );

            _spriteRenderer.sprite = sprite;
        }
        else
        {
            //USAR PLACEHOLDER
            Debug.LogWarning("ScenarioData has no background image.");
        }
    }

    public void SpawnCharacters(List<string> characterIds)
    {
        Debug.Log("SPAWNING ALL CHARACTERs IN SCENARIO");
        foreach (var id in characterIds)
        {
            if (id == GameManager.Instance.PlayerCharacterId) continue;

            var character = GameManager.Instance.GetCharacter(id);
            if (character != null)
                SpawnCharacter(character);
        }
    }

    public void SpawnCharacter(CharacterData character)
    {
        if(character.id == GameManager.Instance.PlayerCharacterId)
            return; // Evitar instanciar al jugador

        if (_characterSpawnArea == null)
        {
            Debug.LogError("Spawn area not set!");
            return;
        }

        Vector2 spawnPoint = FindValidSpawnPoint();

        GameObject characterGO = Instantiate(_characterPrefab, spawnPoint, Quaternion.identity, this.transform);

        float minY = _characterSpawnArea.bounds.min.y;
        float maxY = _characterSpawnArea.bounds.max.y;
        float normalizedY = Mathf.InverseLerp(minY, maxY, spawnPoint.y);
        float scale = Mathf.Lerp(1f, _minCharacterScale, normalizedY);
        characterGO.transform.localScale = Vector3.one * scale;

        _spawnedPositions.Add(spawnPoint);
        _spawnedCharacters[character.id] = characterGO;
        Debug.Log("SPAWNING CHARACTER");
        CharacterView view = characterGO.GetComponent<CharacterView>();
        if (view != null)
        {
            Debug.Log("TRYING TO SET SPRITE RENDERER");
            SpriteRenderer sr = characterGO.GetComponentInChildren<SpriteRenderer>();
            if (sr != null)
            {
                float left = _characterSpawnArea.bounds.min.x;
                float right = _characterSpawnArea.bounds.max.x;
                float threshold = 0.05f * (right - left);

                if (spawnPoint.x - left < threshold)
                {
                    sr.flipX = false; // too much to the left
                }
                else if (right - spawnPoint.x < threshold)
                {
                    sr.flipX = true; // Too much to the right
                }
                else
                {
                    sr.flipX = Random.value < 0.5f; // center then random
                }
            }

            view.Initialize(character);
        }
        else
        {
            Debug.LogError("Character prefab missing CharacterView component.");
        }
    }

    public void ClearCharacters()
    {
        foreach (var go in _spawnedCharacters.Values)
        {
            if (go != null)
                Destroy(go);
        }

        _spawnedCharacters.Clear();
        _spawnedPositions.Clear();
    }

    private Vector2 FindValidSpawnPoint()
    {
        const int maxTries = 30;
        for (int i = 0; i < maxTries; i++)
        {
            Vector2 candidate = GetRandomPointInBox(_characterSpawnArea);
            if (IsFarFromOthers(candidate))
                return candidate;
        }

        // Si no encuentra un punto válido, simplemente devuelve uno
        Debug.LogWarning("SpawnCharacter: couldn't find distant-enough point after 100 tries.");
        return GetRandomPointInBox(_characterSpawnArea);
    }

    private bool IsFarFromOthers(Vector2 candidate)
    {
        foreach (var pos in _spawnedPositions)
        {
            float dx = Mathf.Abs(candidate.x - pos.x);
            float dy = Mathf.Abs(candidate.y - pos.y);
            float weightedDistance = dx + dy * _yWeight;

            if (weightedDistance < _minSpawnDistance)
                return false;
        }
        return true;
    }

    private Vector2 GetRandomPointInBox(BoxCollider2D box)
    {
        Vector2 center = box.bounds.center;
        Vector2 size = box.bounds.size;

        float x = Random.Range(center.x - size.x / 2f, center.x + size.x / 2f);
        float y = Random.Range(center.y - size.y / 2f, center.y + size.y / 2f);

        return new Vector2(x, y);
    }



}

using UnityEngine;

public class ScenarioView : MonoBehaviour
{
    [SerializeField]
    private SpriteRenderer _spriteRenderer;
    [SerializeField]
    private BoxCollider2D _characterSpawnArea;
    [SerializeField] private GameObject _characterPrefab;
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
            Debug.LogWarning("ScenarioData has no background image.");
        }
    }


    public void SpawnCharacter(CharacterData character)
    {
        if (_characterSpawnArea == null)
        {
            Debug.LogError("Spawn area not set!");
            return;
        }

        if (_characterSpawnArea == null)
        {
            Debug.LogError("Spawn area needs a BoxCollider2D component.");
            return;
        }

        Vector2 randomPoint = GetRandomPointInBox(_characterSpawnArea);

        GameObject characterGO = Instantiate(_characterPrefab, randomPoint, Quaternion.identity, this.transform);

        CharacterView view = characterGO.GetComponent<CharacterView>();
        if (view != null)
        {
            view.Initialize(character);
        }
        else
        {
            Debug.LogError("Character prefab missing CharacterView component.");
        }
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

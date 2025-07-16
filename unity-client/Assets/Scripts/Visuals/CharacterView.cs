using UnityEngine;

public class CharacterView : MonoBehaviour
{
    [SerializeField] private SpriteRenderer _spriteRenderer;

    public void Initialize(CharacterData data)
    {
        if (data.portrait != null)
        {
            Sprite sprite = Sprite.Create(
                data.portrait,
                new Rect(0, 0, data.portrait.width, data.portrait.height),
                new Vector2(0.5f, 0f),
                75f
            );

            _spriteRenderer.sprite = sprite;

        }
        else
        {
            // IMATGE PLACEHOLDER
        }

        UpdateSortingOrder();


    }
    private void UpdateSortingOrder()
    {
        _spriteRenderer.sortingOrder = -(int)(transform.position.y * 100);
    }
}


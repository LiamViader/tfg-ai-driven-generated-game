using UnityEngine;

public class CharacterView : MonoBehaviour
{
    [SerializeField] private SpriteRenderer _characterSpriteRenderer;
    [SerializeField] private SpriteRenderer _shadowSpriteRenderer;

    public void Initialize(CharacterData data)
    {
        if (data.portrait != null)
        {
            Sprite sprite = Sprite.Create(
                data.portrait,
                new Rect(0, 0, data.portrait.width, data.portrait.height),
                new Vector2(0.5f, 0f),
                150f
            );

            Vector3 shadowPosition = new Vector3(transform.position.x, transform.position.y+0.2f, transform.position.z);
            _shadowSpriteRenderer.transform.position = shadowPosition;

            _characterSpriteRenderer.sprite = sprite;

            // Medida visual del personaje en unidades del mundo
            float characterWorldWidth = _characterSpriteRenderer.bounds.size.x;

            // Escala base conocida de la sombra
            float baseShadowWidth = _shadowSpriteRenderer.bounds.size.x; // en unidades del mundo también

            // Factor de escala necesario
            float scaleFactor = (characterWorldWidth / baseShadowWidth) * 1.6f;

            // Aplicarlo solo en X
            Vector3 shadowScale = _shadowSpriteRenderer.transform.localScale;
            shadowScale.x *= scaleFactor;
            shadowScale.y *= scaleFactor;
            _shadowSpriteRenderer.transform.localScale = shadowScale;

        }
        else
        {
            // IMATGE PLACEHOLDER
        }

        UpdateSortingOrder();


    }
    private void UpdateSortingOrder()
    {
        _characterSpriteRenderer.sortingOrder = -(int)(transform.position.y * 100);
    }
}


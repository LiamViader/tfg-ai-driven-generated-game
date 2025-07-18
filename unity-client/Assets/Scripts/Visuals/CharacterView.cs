using UnityEngine;

public class CharacterView : MonoBehaviour
{
    [SerializeField] private SpriteRenderer _characterSpriteRenderer;
    [SerializeField] private SpriteRenderer _shadowSpriteRenderer;
    [SerializeField] private Animator _characterAnimator;
    [SerializeField] private HandleCharacterMaterial _materialHandler;
    [SerializeField] private CharacterContextualUI _characterContextualUI;
    [SerializeField] private Transform _contextualMenuOriginRight;
    [SerializeField] private Transform _contextualMenuOriginLeft;

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
            _materialHandler.SetMaterialToSprite(_characterSpriteRenderer);
            UpdateColliderToMatchSprite(sprite);
            UpdateContextualMenuOrigins();
        }
        else
        {
            // IMATGE PLACEHOLDER
        }

        UpdateSortingOrder();


    }

    private void UpdateColliderToMatchSprite(Sprite sprite)
    {
        BoxCollider2D collider = _characterSpriteRenderer.GetComponent<BoxCollider2D>();
        if (collider == null) collider = _characterSpriteRenderer.gameObject.AddComponent<BoxCollider2D>();
        collider.offset = Vector2.zero;

        collider.isTrigger = true;


        collider.size = sprite.bounds.size;
        collider.offset = new Vector2(0, collider.size.y/2);
    }

    private void UpdateContextualMenuOrigins()
    {
        Bounds bounds = _characterSpriteRenderer.bounds;

        Vector3 topLeft = new Vector3(bounds.min.x-0.2f, bounds.max.y-0.5f, transform.position.z);
        Vector3 topRight = new Vector3(bounds.max.x +0.2f, bounds.max.y-0.5f, transform.position.z);

        if (_contextualMenuOriginLeft != null)
            _contextualMenuOriginLeft.position = topLeft;

        if (_contextualMenuOriginRight != null)
            _contextualMenuOriginRight.position = topRight;
    }


    private void UpdateSortingOrder()
    {
        _characterSpriteRenderer.sortingOrder = -(int)(transform.position.y * 100);
    }


    public void OnClick()
    {
        _characterAnimator.SetTrigger("ClickTrigger");
        ShowContextualMenu();
    }

    public void ShowContextualMenu()
    {
        _characterContextualUI.ShowContextualMenu(_contextualMenuOriginRight);
    }

    

}


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

    public string CharacterId { get; private set; }
    public void Initialize(CharacterData data)
    {
        CharacterId = data.id;

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

        if (_characterContextualUI != null)
        {
            _characterContextualUI.Initialize(CharacterId);
            // Si UIManager centraliza el registro, llama a UIManager para registrar este UI
            UIManager.Instance.RegisterCharacterContextualUI(CharacterId, _characterContextualUI);
        }
        else
        {
            Debug.LogError($"CharacterContextualUI not assigned for character {data.id} in CharacterView.");
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

    void OnDestroy()
    {
        if (UIManager.Instance != null && _characterContextualUI != null)
        {
            UIManager.Instance.UnregisterCharacterContextualUI(CharacterId);
        }
    }

    public void OnClick()
    {
        _characterAnimator.SetTrigger("ClickTrigger");
        ShowContextualMenu();
    }

    public void ShowContextualMenu()
    {
        Vector2 origin = _characterSpriteRenderer.bounds.center;
        Vector2 size = _characterSpriteRenderer.bounds.size * 0.8f;
        float maxDistance = 100f;
        int characterLayerMask = LayerMask.GetMask("Characters");
        float minDistance = 6f;

        bool facingRight = !_characterSpriteRenderer.flipX;

        float rightCharDist = GetRawCharacterDistance(origin, size, Vector2.right, maxDistance, characterLayerMask);
        float leftCharDist = GetRawCharacterDistance(origin, size, Vector2.left, maxDistance, characterLayerMask);
        float rightCamDist = GetDistanceToCameraEdge(origin, Vector2.right, maxDistance);
        float leftCamDist = GetDistanceToCameraEdge(origin, Vector2.left, maxDistance);
        float rightFinalDist = Mathf.Min(rightCharDist, rightCamDist);
        float leftFinalDist = Mathf.Min(leftCharDist, leftCamDist);


        if (facingRight && rightFinalDist > minDistance)
        {
            _characterContextualUI.ShowContextualMenu(_contextualMenuOriginRight, true);
            return;
        }

        if (!facingRight && leftFinalDist > minDistance)
        {
            _characterContextualUI.ShowContextualMenu(_contextualMenuOriginLeft, false);
            return;
        }


        bool rightHitsCam = rightCamDist < minDistance;
        bool leftHitsCam = leftCamDist < minDistance;

        bool originalFlipX = _characterSpriteRenderer.flipX;

        if (!rightHitsCam && leftHitsCam)
        {
            _characterSpriteRenderer.flipX = false;
            _characterContextualUI.ShowContextualMenu(_contextualMenuOriginRight, true, () =>
            {
                _characterSpriteRenderer.flipX = originalFlipX;
            });
        }
        else if (!leftHitsCam && rightHitsCam)
        {
            _characterSpriteRenderer.flipX = true;
            _characterContextualUI.ShowContextualMenu(_contextualMenuOriginLeft, false, () =>
            {
                _characterSpriteRenderer.flipX = originalFlipX;
            });
        }
        else
        {
            if (rightFinalDist >= leftFinalDist)
            {
                _characterSpriteRenderer.flipX = false;
                _characterContextualUI.ShowContextualMenu(_contextualMenuOriginRight, true, () =>
                {
                    _characterSpriteRenderer.flipX = originalFlipX;
                });
            }
            else
            {
                _characterSpriteRenderer.flipX = true;
                _characterContextualUI.ShowContextualMenu(_contextualMenuOriginLeft, false, () =>
                {
                    _characterSpriteRenderer.flipX = originalFlipX;
                });
            }
        }
    }

    private float GetRawCharacterDistance(Vector2 origin, Vector2 size, Vector2 direction, float maxDistance, int layerMask)
    {
        RaycastHit2D[] hits = Physics2D.BoxCastAll(origin, size, 0f, direction, maxDistance, layerMask);

        foreach (var hit in hits)
        {
            if (hit.collider != null && hit.collider.gameObject != _characterSpriteRenderer.gameObject)
            {
                return hit.distance;
            }
        }

        return maxDistance;
    }


    private float GetDistanceToCameraEdge(Vector2 origin, Vector2 direction, float maxDistance)
    {
        Camera cam = Camera.main;
        if (cam == null) return maxDistance;

        float worldX = origin.x;
        float worldY = origin.y;
        float camZ = cam.transform.position.z;

        // Convertimos el punto al espacio de viewport
        Vector3 viewportPoint = cam.WorldToViewportPoint(new Vector3(worldX, worldY, 0f));

        // Obtenemos el punto del borde derecho o izquierdo de la cámara en coordenadas de mundo
        float edgeX = (direction == Vector2.right)
            ? cam.ViewportToWorldPoint(new Vector3(1f, viewportPoint.y, cam.nearClipPlane)).x
            : cam.ViewportToWorldPoint(new Vector3(0f, viewportPoint.y, cam.nearClipPlane)).x;

        return Mathf.Abs(edgeX - worldX);
    }





}


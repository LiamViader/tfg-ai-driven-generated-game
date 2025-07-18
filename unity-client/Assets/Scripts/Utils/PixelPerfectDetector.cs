using UnityEngine;

[RequireComponent(typeof(SpriteRenderer))]
[RequireComponent(typeof(Collider2D))]
public class PixelPerfectDetector : MonoBehaviour
{
    private SpriteRenderer spriteRenderer;

    [Tooltip("The alpha threshold for a pixel to be considered 'clickable'.")]
    [SerializeField] private float alphaThreshold = 0.1f;
    [SerializeField] private CharacterView _characterView;

    void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
    }



    public void ClickCharacter()
    {
        _characterView.OnClick();
    }

    /// <summary>
    /// Comprueba si en una posición específica del mundo hay un píxel visible de este sprite.
    /// Este método es AHORA PÚBLICO para que otros scripts puedan llamarlo.
    /// </summary>
    /// <param name="worldPosition">La posición en el mundo a comprobar (ej. la del ratón).</param>
    /// <returns>True si el píxel en esa posición no es transparente.</returns>
    public bool IsPixelVisibleAt(Vector3 worldPosition)
    {
        if (spriteRenderer.sprite == null) return false;

        // Convertir la posición del mundo a la posición local del sprite
        Vector2 localPos = transform.InverseTransformPoint(worldPosition);

        // Obtener la información del sprite
        Sprite sprite = spriteRenderer.sprite;
        Texture2D texture = sprite.texture;
        Rect spriteRect = sprite.textureRect;

        // Calcular la coordenada del píxel correspondiente
        float pixelsPerUnit = sprite.pixelsPerUnit;
        Vector2 pivot = sprite.pivot;

        int pixelX = Mathf.FloorToInt(spriteRect.x + localPos.x * pixelsPerUnit + pivot.x);
        int pixelY = Mathf.FloorToInt(spriteRect.y + localPos.y * pixelsPerUnit + pivot.y);

        // Comprobar si las coordenadas están dentro de la textura
        if (pixelX < 0 || pixelX >= texture.width || pixelY < 0 || pixelY >= texture.height)
        {
            return false;
        }

        // Obtener el color del píxel y comprobar su transparencia
        try
        {
            Color pixelColor = texture.GetPixel(pixelX, pixelY);
            return pixelColor.a > alphaThreshold;
        }
        catch (UnityException e)
        {
            // Este error ocurre si la textura no tiene "Read/Write" activado.
            Debug.LogError($"Error al leer píxel en '{gameObject.name}'. ¿La textura se cargó como 'leíble'? Error: {e.Message}");
            return false;
        }
    }
}
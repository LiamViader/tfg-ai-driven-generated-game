using UnityEngine;

// Requiere que el GameObject tenga estos dos componentes.
[RequireComponent(typeof(SpriteRenderer))]
[RequireComponent(typeof(Collider2D))]
public class PixelPerfectDetector : MonoBehaviour
{
    private SpriteRenderer spriteRenderer;

    // Puedes ajustar este umbral. Un valor > 0 significa que el píxel no es totalmente transparente.
    [Tooltip("The alpha threshold for a pixel to be considered 'clickable'.")]
    [SerializeField] private float alphaThreshold = 0.1f;

    void Awake()
    {
        // Guardamos una referencia al SpriteRenderer para no tener que buscarlo cada vez.
        spriteRenderer = GetComponent<SpriteRenderer>();
    }

    /// <summary>
    /// Este método de Unity se llama automáticamente cuando se hace clic
    /// en cualquier Collider2D de este GameObject.
    /// </summary>
    void OnMouseDown()
    {
        if (IsClickOnVisiblePixel())
        {
            // ¡El clic fue en una parte visible del personaje!
            // Aquí pones lo que quieres que pase.
            Debug.Log($"CLICK PRECISO sobre {gameObject.name}!");
        }
        else
        {
            Debug.Log($"Clic en el área de {gameObject.name}, pero en una zona transparente.");
        }
    }

    /// <summary>
    /// Comprueba si el clic del ratón actual está sobre un píxel no transparente del sprite.
    /// </summary>
    private bool IsClickOnVisiblePixel()
    {
        // 1. Convertir la posición del ratón en la pantalla a la posición en el mundo del juego
        Vector3 mouseWorldPos = Camera.main.ScreenToWorldPoint(Input.mousePosition);

        // 2. Convertir la posición del mundo a la posición local del sprite
        Vector2 localPos = transform.InverseTransformPoint(mouseWorldPos);

        // 3. Obtener la información del sprite
        Sprite sprite = spriteRenderer.sprite;
        Texture2D texture = sprite.texture;
        Rect spriteRect = sprite.textureRect; // El área del sprite dentro de la textura total

        // 4. Calcular la coordenada del píxel correspondiente a la posición local
        // Esto convierte las unidades de Unity a píxeles de la textura
        float pixelsPerUnit = sprite.pixelsPerUnit;
        Vector2 pivot = sprite.pivot;

        // Calculamos la coordenada del píxel desde la esquina inferior izquierda de la textura
        int pixelX = Mathf.FloorToInt(spriteRect.x + localPos.x * pixelsPerUnit + pivot.x);
        int pixelY = Mathf.FloorToInt(spriteRect.y + localPos.y * pixelsPerUnit + pivot.y);

        // 5. Comprobar si las coordenadas están dentro de los límites de la textura
        if (pixelX < 0 || pixelX >= texture.width || pixelY < 0 || pixelY >= texture.height)
        {
            return false; // El clic está fuera de la textura
        }

        // 6. Obtener el color del píxel y comprobar su transparencia (alfa)
        Color pixelColor = texture.GetPixel(pixelX, pixelY);
        return pixelColor.a > alphaThreshold;
    }
}
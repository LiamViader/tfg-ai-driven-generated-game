using UnityEngine;

// Requiere que el GameObject tenga estos dos componentes.
[RequireComponent(typeof(SpriteRenderer))]
[RequireComponent(typeof(Collider2D))]
public class PixelPerfectDetector : MonoBehaviour
{
    private SpriteRenderer spriteRenderer;

    // Puedes ajustar este umbral. Un valor > 0 significa que el p�xel no es totalmente transparente.
    [Tooltip("The alpha threshold for a pixel to be considered 'clickable'.")]
    [SerializeField] private float alphaThreshold = 0.1f;

    void Awake()
    {
        // Guardamos una referencia al SpriteRenderer para no tener que buscarlo cada vez.
        spriteRenderer = GetComponent<SpriteRenderer>();
    }

    /// <summary>
    /// Este m�todo de Unity se llama autom�ticamente cuando se hace clic
    /// en cualquier Collider2D de este GameObject.
    /// </summary>
    void OnMouseDown()
    {
        if (IsClickOnVisiblePixel())
        {
            // �El clic fue en una parte visible del personaje!
            // Aqu� pones lo que quieres que pase.
            Debug.Log($"CLICK PRECISO sobre {gameObject.name}!");
        }
        else
        {
            Debug.Log($"Clic en el �rea de {gameObject.name}, pero en una zona transparente.");
        }
    }

    /// <summary>
    /// Comprueba si el clic del rat�n actual est� sobre un p�xel no transparente del sprite.
    /// </summary>
    private bool IsClickOnVisiblePixel()
    {
        // 1. Convertir la posici�n del rat�n en la pantalla a la posici�n en el mundo del juego
        Vector3 mouseWorldPos = Camera.main.ScreenToWorldPoint(Input.mousePosition);

        // 2. Convertir la posici�n del mundo a la posici�n local del sprite
        Vector2 localPos = transform.InverseTransformPoint(mouseWorldPos);

        // 3. Obtener la informaci�n del sprite
        Sprite sprite = spriteRenderer.sprite;
        Texture2D texture = sprite.texture;
        Rect spriteRect = sprite.textureRect; // El �rea del sprite dentro de la textura total

        // 4. Calcular la coordenada del p�xel correspondiente a la posici�n local
        // Esto convierte las unidades de Unity a p�xeles de la textura
        float pixelsPerUnit = sprite.pixelsPerUnit;
        Vector2 pivot = sprite.pivot;

        // Calculamos la coordenada del p�xel desde la esquina inferior izquierda de la textura
        int pixelX = Mathf.FloorToInt(spriteRect.x + localPos.x * pixelsPerUnit + pivot.x);
        int pixelY = Mathf.FloorToInt(spriteRect.y + localPos.y * pixelsPerUnit + pivot.y);

        // 5. Comprobar si las coordenadas est�n dentro de los l�mites de la textura
        if (pixelX < 0 || pixelX >= texture.width || pixelY < 0 || pixelY >= texture.height)
        {
            return false; // El clic est� fuera de la textura
        }

        // 6. Obtener el color del p�xel y comprobar su transparencia (alfa)
        Color pixelColor = texture.GetPixel(pixelX, pixelY);
        return pixelColor.a > alphaThreshold;
    }
}
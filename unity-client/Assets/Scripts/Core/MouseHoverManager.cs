using UnityEngine;
using System.Linq;

public class MouseHoverManager : MonoBehaviour
{
    private PixelPerfectDetector lastHoveredCharacter = null;
    private int characterLayerMask;

    void Start()
    {
        characterLayerMask = LayerMask.GetMask("Characters");
    }

    void Update()
    {
        // 1. Primero, determinamos cuál es el personaje bajo el ratón en ESTE frame.
        PixelPerfectDetector currentlyHovered = FindTopmostVisibleCharacter();

        // 2. Ahora, y solo ahora, comparamos el resultado actual con el del frame anterior.
        if (currentlyHovered != lastHoveredCharacter)
        {
            // Hubo un cambio de estado.

            // Si antes estábamos sobre un personaje, llamamos a su evento de salida.
            if (lastHoveredCharacter != null)
            {
                OnHoverEnd(lastHoveredCharacter);
            }

            // Si ahora estamos sobre un personaje nuevo, llamamos a su evento de entrada.
            if (currentlyHovered != null)
            {
                OnHoverStart(currentlyHovered);
            }

            // 3. Finalmente, actualizamos el estado para el próximo frame.
            lastHoveredCharacter = currentlyHovered;
        }
    }

    /// <summary>
    /// Encuentra el personaje visible que está más arriba bajo el cursor del ratón.
    /// Devuelve su componente PixelPerfectDetector, o null si no hay ninguno.
    /// </summary>
    private PixelPerfectDetector FindTopmostVisibleCharacter()
    {
        Vector2 mouseWorldPos = Camera.main.ScreenToWorldPoint(Input.mousePosition);
        RaycastHit2D[] hits = Physics2D.RaycastAll(mouseWorldPos, Vector2.zero, Mathf.Infinity, characterLayerMask);

        if (hits.Length == 0)
        {
            return null; // No hemos golpeado nada en la capa de personajes.
        }

        // Ordenamos los resultados para procesar primero los que están más arriba (mayor sortingOrder).
        var sortedHits = hits.OrderByDescending(h => h.collider.GetComponent<SpriteRenderer>()?.sortingOrder ?? 0);

        // Buscamos el primero que pase la prueba de píxeles.
        foreach (var hit in sortedHits)
        {
            if (hit.collider.TryGetComponent(out PixelPerfectDetector detector))
            {
                if (detector.IsPixelVisibleAt(mouseWorldPos))
                {
                    return detector; // ¡Encontrado! Devolvemos este y terminamos.
                }
            }
        }

        // Hemos golpeado colliders, pero todos en zonas transparentes.
        return null;
    }

    /// <summary>
    /// Lógica que se ejecuta cuando el ratón entra en un personaje.
    /// </summary>
    private void OnHoverStart(PixelPerfectDetector character)
    {
        Debug.Log($"HOVER START on {character.name}");
        // Aquí puedes añadir efectos visuales, como cambiar el material.
        HandleCharacterMaterial material_handler = character.GetComponent<HandleCharacterMaterial>();
        if (material_handler != null)
        {
            material_handler.SetHoverStrength(1f);
        }
    }

    /// <summary>
    /// Lógica que se ejecuta cuando el ratón sale de un personaje.
    /// </summary>
    private void OnHoverEnd(PixelPerfectDetector character)
    {
        Debug.Log($"HOVER END on {character.name}");
        // Revertimos los efectos visuales.
        HandleCharacterMaterial material_handler = character.GetComponent<HandleCharacterMaterial>();
        if (material_handler != null)
        {
            material_handler.SetHoverStrength(0f);
        }
    }
}
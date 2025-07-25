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
        PixelPerfectDetector currentlyHovered = FindTopmostVisibleCharacter();

        if (currentlyHovered != lastHoveredCharacter)
        {

            if (lastHoveredCharacter != null)
            {
                OnHoverEnd(lastHoveredCharacter);
            }

            if (currentlyHovered != null)
            {
                OnHoverStart(currentlyHovered);
            }

            lastHoveredCharacter = currentlyHovered;
        }

        if (Input.GetMouseButtonDown(0) && currentlyHovered != null)
        {
            currentlyHovered.ClickCharacter();
        }
    }


    private PixelPerfectDetector FindTopmostVisibleCharacter()
    {
        Vector2 mouseWorldPos = Camera.main.ScreenToWorldPoint(Input.mousePosition);
        RaycastHit2D[] hits = Physics2D.RaycastAll(mouseWorldPos, Vector2.zero, Mathf.Infinity, characterLayerMask);

        if (hits.Length == 0)
        {
            return null;
        }

        var sortedHits = hits.OrderByDescending(h => h.collider.GetComponent<SpriteRenderer>()?.sortingOrder ?? 0);


        foreach (var hit in sortedHits)
        {
            if (hit.collider.TryGetComponent(out PixelPerfectDetector detector))
            {
                if (detector.IsPixelVisibleAt(mouseWorldPos))
                {
                    return detector;
                }
            }
        }

        return null;
    }

    private void OnHoverStart(PixelPerfectDetector character)
    {
        HandleCharacterMaterial material_handler = character.GetComponent<HandleCharacterMaterial>();
        if (material_handler != null)
        {
            material_handler.SetHoverStrength(1f);
        }
    }


    private void OnHoverEnd(PixelPerfectDetector character)
    {
        HandleCharacterMaterial material_handler = character.GetComponent<HandleCharacterMaterial>();
        if (material_handler != null)
        {
            material_handler.SetHoverStrength(0f);
        }
    }
}
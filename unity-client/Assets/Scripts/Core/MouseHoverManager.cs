using UnityEngine;

public class MouseHoverManager : MonoBehaviour
{
    private PixelPerfectDetector lastHoveredCharacter = null;

    void Update()
    {
        Vector2 mouseWorldPos = Camera.main.ScreenToWorldPoint(Input.mousePosition);
        RaycastHit2D hit = Physics2D.Raycast(mouseWorldPos, Vector2.zero);

        PixelPerfectDetector currentDetector = null;

        if (hit.collider != null)
        {
            hit.collider.TryGetComponent(out currentDetector);
        }

        if (currentDetector != lastHoveredCharacter)
        {
            if (lastHoveredCharacter != null)
            {
                Debug.Log($"HOVER END on {lastHoveredCharacter.name}");
            }

            if (currentDetector != null)
            {
                Debug.Log($"HOVER START on {currentDetector.name}");
            }

            lastHoveredCharacter = currentDetector;
        }
    }
}
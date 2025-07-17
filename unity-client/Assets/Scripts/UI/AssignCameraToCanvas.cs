using UnityEngine;

public class AssignCameraToCanvas : MonoBehaviour
{
    [SerializeField] private Canvas targetCanvas;

    void Awake()
    {
        if (targetCanvas != null && Camera.main != null)
        {
            targetCanvas.worldCamera = Camera.main;
        }
    }

    public void Assign()
    {
        if (targetCanvas != null && Camera.main != null)
        {
            targetCanvas.worldCamera = Camera.main;
        }
    }
}

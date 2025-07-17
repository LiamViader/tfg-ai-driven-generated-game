using UnityEngine;

[ExecuteAlways]
[RequireComponent(typeof(Camera))]
public class FixedAspectCamera : MonoBehaviour
{
    [Header("Target aspect ratio")]
    [SerializeField] private Vector2 targetAspectRatio = new Vector2(16, 9);

    [Header("Scenario settings")]
    [SerializeField] private float scenarioHeightInPixels = 1440f;
    [SerializeField] private float pixelsPerUnit = 100;

    private Camera _camera;

    void Awake()
    {
        _camera = GetComponent<Camera>();
        UpdateViewport();
    }

#if UNITY_EDITOR
    void Update()
    {
        if (!Application.isPlaying)
            UpdateViewport();
    }
#endif

    void UpdateViewport()
    {
        if (_camera == null)
            _camera = GetComponent<Camera>();

        // 1. Calcular height del escenario en unidades
        float scenarioHeightInUnits = scenarioHeightInPixels / pixelsPerUnit;
        _camera.orthographicSize = scenarioHeightInUnits / 2f;

    }
}

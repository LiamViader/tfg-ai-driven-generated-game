using UnityEngine;
using System.Collections.Generic;

public class AssignCameraToCanvas : MonoBehaviour
{
    [SerializeField] private List<Canvas> targetCanvas;

    void Awake()
    {
        Assign(); // Llama al m�todo en Awake tambi�n
    }

    public void Assign()
    {
        if (Camera.main == null || targetCanvas == null) return;

        foreach (var canvas in targetCanvas)
        {
            if (canvas != null)
                canvas.worldCamera = Camera.main;
        }
    }
}
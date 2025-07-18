using UnityEngine;

public class CharacterContextualUI : MonoBehaviour
{
    [SerializeField] private Canvas _canvas;
    private void OnEnable()
    {
        if (_canvas != null && Camera.main != null)
        {
            _canvas.worldCamera = Camera.main;
        }
    }

    public void ShowContextualMenu(Transform contextualMenuOrigin)
    {
        if (_canvas == null) return;

        _canvas.gameObject.SetActive(true);

        _canvas.transform.SetParent(contextualMenuOrigin, worldPositionStays: false);

        _canvas.transform.localPosition = Vector3.zero;
        _canvas.transform.localRotation = Quaternion.identity;
        _canvas.transform.localScale = Vector3.one;
    }

}

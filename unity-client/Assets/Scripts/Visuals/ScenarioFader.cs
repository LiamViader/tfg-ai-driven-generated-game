using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class ScenarioFader : MonoBehaviour
{
    private List<Renderer> _renderers = new();
    private bool _renderersSet = false;
    public void SetAlpha(float alpha)
    {
        if (!_renderersSet)
        {
            GetComponentsInChildren(true, _renderers);
            _renderersSet = true;
        }
        foreach (var renderer in _renderers)
        {
            if (renderer.material.HasProperty("_Color"))
            {
                Color c = renderer.material.color;
                c.a = alpha;
                renderer.material.color = c;
            }
        }
    }

    public Coroutine FadeTo(float targetAlpha, float duration, System.Action onComplete = null)
    {
        if (!_renderersSet)
        {
            GetComponentsInChildren(true, _renderers);
            _renderersSet = true;
        }

        return StartCoroutine(FadeRoutine(targetAlpha, duration, onComplete));
    }

    private IEnumerator FadeRoutine(float targetAlpha, float duration, System.Action onComplete)
    {
        float time = 0f;
        float startAlpha = _renderers.Count > 0 ? _renderers[0].material.color.a : 1f;

        while (time < duration)
        {
            time += Time.deltaTime;
            float alpha = Mathf.Lerp(startAlpha, targetAlpha, time / duration);
            SetAlpha(alpha);
            yield return null;
        }

        SetAlpha(targetAlpha);
        onComplete?.Invoke();
    }
}

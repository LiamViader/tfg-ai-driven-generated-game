using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class ScenarioFader : MonoBehaviour
{
    private List<Renderer> _renderers = new();
    private List<CanvasGroup> _canvasGroups = new();
    private bool _componentsCollected = false;
    public void SetAlpha(float alpha)
    {
        if (!_componentsCollected)
        {
            CollectComponents();
        }
        foreach (var renderer in _renderers)
        {
            if (renderer.material.HasProperty("_Color"))
            {
                Color c = renderer.material.color;
                c.a = alpha;
                renderer.material.color = c;
            }
            if (renderer.material.HasProperty("_AlphaOverride"))
            {
                renderer.material.SetFloat("_AlphaOverride", alpha);
            }
        }
        foreach (var cg in _canvasGroups)
        {
            cg.alpha = alpha;
        }
    }

    public Coroutine FadeTo(float targetAlpha, float duration, System.Action onComplete = null)
    {
        if (!_componentsCollected)
        {
            CollectComponents();
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
    private void CollectComponents()
    {
        GetComponentsInChildren(true, _renderers);
        GetComponentsInChildren(true, _canvasGroups);
        _componentsCollected = true;
    }
}

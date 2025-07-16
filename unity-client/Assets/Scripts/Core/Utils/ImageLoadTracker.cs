using System;
using UnityEngine;
using System.Collections;
public class ImageLoadTracker : MonoBehaviour
{
    public static ImageLoadTracker Instance;

    private int _pendingCount = 0;
    private Action _onAllLoaded;

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    public void TrackImageLoad(IEnumerator coroutine)
    {
        _pendingCount++;
        StartCoroutine(WrapCoroutine(coroutine));
    }

    public void OnAllImagesLoaded(Action callback)
    {
        if (_pendingCount == 0)
            callback?.Invoke();
        else
            _onAllLoaded = callback;
    }

    private IEnumerator WrapCoroutine(IEnumerator routine)
    {
        yield return routine;
        _pendingCount--;

        if (_pendingCount == 0)
            _onAllLoaded?.Invoke();
    }
}

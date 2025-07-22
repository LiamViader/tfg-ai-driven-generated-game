using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using System.Collections;
using DG.Tweening;

public class TextlogManager : MonoBehaviour
{
    [SerializeField] private TMP_Text _characterNameTextLeft;
    [SerializeField] private TMP_Text _characterNameTextRight;
    [SerializeField] private GameObject _characterNameLeft;
    [SerializeField] private GameObject _characterNameRight;

    public void UpdateLeftName(string text, bool show)
    {
        _characterNameTextLeft.text = text;
        _characterNameLeft.SetActive(show);
    }

    public void UpdateRightName(string text, bool show)
    {
        _characterNameTextRight.text = text;
        _characterNameRight.SetActive(show);
    }
}

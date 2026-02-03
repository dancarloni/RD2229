VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmSplash 
   Caption         =   "SezioniCA.Az"
   ClientHeight    =   4515
   ClientLeft      =   96
   ClientTop       =   516
   ClientWidth     =   10224
   OleObjectBlob   =   "frmSplash.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmSplash"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub CommandButton1_Click()
Unload frmSplash
End Sub

Private Sub UserForm_Initialize()
Caption = VersioneSw
End Sub

; Script to open Spotify and start playback

Run("explorer shell:appsFolder\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify")

; Wait for Spotify to open
Sleep(3000)  ; Adjust this if Spotify takes longer to open

; Send the Play/Pause media key
Send("{Media_Play_Pause}")
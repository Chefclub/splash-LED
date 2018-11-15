module Main exposing (main)

import Browser
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Http
import Json.Decode as Decode
import Json.Encode as Encode


botUrl =
    "https://networks-monitoring.chefclub.tools/v1/splash-led-bot"


type alias Flags =
    {}


type alias Model =
    { message : String
    }


type alias MessageStatus =
    String


type Msg
    = NewMessage String
    | SendMessage
    | LoadMessageStatus (Result Http.Error MessageStatus)


init : Flags -> ( Model, Cmd Msg )
init flags =
    ( { message = "" }, Cmd.none )


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        NewMessage message ->
            ( { model | message = message }, Cmd.none )

        SendMessage ->
            ( model
            , sendMessage model.message
            )

        LoadMessageStatus (Ok response) ->
            ( { model | message = "" }
            , Cmd.none
            )

        LoadMessageStatus (Err err) ->
            let
                _ =
                    Debug.log "Error while sending the message" err
            in
            ( model, Cmd.none )


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none


view : Model -> Html Msg
view model =
    article [ id "splash", class "panel" ]
        [ header [] [ h2 [] [ text "Send me a message" ] ]
        , Html.form [ onSubmit SendMessage ]
            [ input
                [ placeholder "Enter your message and press enter to send it"
                , autofocus True
                , style "width" "100%"
                , style "padding" "5px"
                , onInput NewMessage
                , value model.message
                ]
                []
            , br [] []
            , if model.message /= "" then
                button [ type_ "button", onClick SendMessage ] [ text "Send" ]

              else
                div [] []
            ]
        ]


main : Program Flags Model Msg
main =
    Browser.element
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }


buildMultipartBody : String -> Http.Body
buildMultipartBody message =
    Http.multipartBody
        [ Http.stringPart "text" message
        ]


sendMessage : String -> Cmd Msg
sendMessage message =
    Http.request
        { method = "POST"
        , headers = []
        , url = botUrl
        , body = buildMultipartBody message
        , expect = Http.expectString LoadMessageStatus
        , timeout = Nothing
        , tracker = Nothing
        }

const express = require('express')
const axios = require('axios')
const queryString = require('query-string')
const cookieParser = require('cookie-parser')
const cors = require('cors')
const SpotifyWebApi = require('spotify-web-api-node');
require('dotenv').config()

/**
 *
 */
const playlists = {}

/**
 * Express App
 */
const app = express()
app.use(cors({ origin: true, credentials: true }))
app.use(cookieParser())

/**
 * Spotify parameters
 */
const client_id = process.env.client_id || ''
const client_secret = process.env.client_secret || ''
const redirect_uri = 'http://localhost:3000/auth/spotify/callback'

/**
 *
 * @param {*} length
 * @returns
 */
function generateRandomString(length) {
  var text = ''
  var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

  for (var i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length))
  }

  return text
}

/**
 * Spotify Login routes
 */
app.get('/auth/spotify/', (req, res) => {
  const scope = 'user-read-private user-read-email user-top-read'
  const state = generateRandomString(16)

  res.cookie('spotify_auth_state', state)

  res.redirect('https://accounts.spotify.com/authorize?' +
    queryString.stringify({
      response_type: 'code',
      client_id: client_id,
      scope: scope,
      redirect_uri: redirect_uri,
      state: state
    })
  )
})

app.get('/auth/spotify/callback', (req, res) => {
  // your application requests refresh and access tokens
  // after checking the state parameter
  const code = req.query.code || null
  const state = req.query.state || null
  const storedState = req.cookies ? req.cookies['spotify_auth_state'] : null
  const storedRedirect = req.cookies ? req.cookies['redirect'] : null

  if (state === null || state !== storedState) {
    res.redirect('/#' +
      queryString.stringify({
        error: 'state_mismatch'
      }))
  } else {
    res.clearCookie('spotify_auth_state')

    const headers = {
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      auth: {
        username: client_id,
        password: client_secret,
      },
    }
    const data = {
      grant_type: 'authorization_code',
      code: code,
      redirect_uri: redirect_uri,
    }

    axios.post('https://accounts.spotify.com/api/token', queryString.stringify(data), headers).then((response) => {
      const access_token = response.data.access_token
      const refresh_token = response.data.refresh_token

      // use the access token to access the Spotify Web API
      res.cookie('access_token', access_token, { maxAge: 900000, httpOnly: true })
      res.cookie('refresh_token', refresh_token, { maxAge: 900000, httpOnly: true })

      if (storedRedirect == null) {
        res.redirect('/#login_sucessful')
      } else {
        res.redirect(storedRedirect)
        res.clearCookie('redirect')
      }
      res.send(response.data)
    })
      .catch((error) => {
        console.log(error)
        res.send({
          status: 'error'
        })
      })
  }
})

app.get('/refresh_token', (req, res) => {
  // requesting access token from refresh token
  const refresh_token = req.query.refresh_token
  const authOptions = {
    url: 'https://accounts.spotify.com/api/token',
    headers: { 'Authorization': 'Basic ' + (Buffer.from(client_id + ':' + client_secret).toString('base64')) },
    form: {
      grant_type: 'refresh_token',
      refresh_token: refresh_token
    },
    json: true
  }

  axios({
    method: 'post',
    url: authOptions.url,
    headers: authOptions.headers,
    data: authOptions.form
  }).then(response => {
    if (response.status === 200) {
      res.send(response.data)
    }
  })

  res.send('error')
})

/**
 * Playlists route
 */
app.get('/playlist/new', async (req, res) => {
  const storedAcessToken = req.cookies ? req.cookies['access_token'] : null
  const storedRefreshToken = req.cookies ? req.cookies['refresh_token'] : null

  if (storedAcessToken == null || storedRefreshToken == null) {
    res.cookie('redirect', '/playlist/new')
    res.redirect('/auth/spotify/')
  } else {
    const playlistId = generateRandomString(16)

    while (playlists[playlistId] != null) {
      playlistId = generateRandomString(16)
    }

    playlists[playlistId] = {}

    // Get user name
    const options = {
      url: 'https://api.spotify.com/v1/me',
      headers: { 'Authorization': 'Bearer ' + storedAcessToken },
      json: true
    }

    const spotifyApi = new SpotifyWebApi({
      clientId: client_id,
      clientSecret: client_secret,
      redirectUri: redirect_uri
    })

    spotifyApi.setAccessToken(storedAcessToken)
    spotifyApi.setRefreshToken(storedRefreshToken)

    try {
      const [topTracks, tracksFeatures] = await getTopTracks(spotifyApi)
      let me = (await spotifyApi.getMe()).body
      playlists[playlistId][storedAcessToken] = {
        name: me.display_name,
        refresh_token: storedRefreshToken,
        top_tracks: topTracks,
        tracks_features: tracksFeatures
      }
    } catch (err) {
      res.send({
        status: 'error',
        error: err,
      })
    }

    res.redirect('/playlist/' + playlistId)
  }

})

app.get('/playlist/has/:id', (req, res) => {
  const playlistId = req.params.id

  if (playlists[playlistId] != null) {
    res.send({
      status: 'ok',
      users: playlists[playlistId]
    })
  } else {
    res.send({
      status: 'error',
      error: 'Playlist not found'
    })
  }
})

app.get('/playlist/add_on/:id', async (req, res) => {
  const storedAcessToken = req.cookies ? req.cookies['access_token'] : null
  const storedRefreshToken = req.cookies ? req.cookies['refresh_token'] : null

  if (storedAcessToken == null || storedRefreshToken == null) {
    res.cookie('redirect', '/playlist/add_on/' + req.params.id)
    res.redirect('/auth/spotify/')
  } else {
    const playlistId = req.params.id
    if (playlists[playlistId] == null) {
      res.send({
        status: 'error',
        error: 'No playlist'
      })
    } else {
      if (playlists[playlistId][storedAcessToken] == null) {
        const spotifyApi = new SpotifyWebApi({
          clientId: client_id,
          clientSecret: client_secret,
          redirectUri: redirect_uri
        })
        spotifyApi.setAccessToken(storedAcessToken)
        spotifyApi.setRefreshToken(storedRefreshToken)

        try {
          const [topTracks, tracksFeatures] = await getTopTracks(spotifyApi)
          let me = (await spotifyApi.getMe()).body
          playlists[playlistId][storedAcessToken] = {
            name: me.display_name,
            refresh_token: storedRefreshToken,
            top_tracks: topTracks,
            tracks_features: tracksFeatures
          }
        } catch (err) {
          res.send({
            status: 'error',
            error: err,
          })
        }
      }
      res.redirect('/playlist/' + playlistId)
    }
  }
})

app.get('/playlist/generate/:id', async (req, res) => {
  const storedAcessToken = req.cookies ? req.cookies['access_token'] : null
  const storedRefreshToken = req.cookies ? req.cookies['refresh_token'] : null

  if (storedAcessToken == null || storedRefreshToken == null) {
    res.cookie('redirect', '/playlist/generate/' + req.params.id)
    res.redirect('/auth/spotify/')
  } else {

    const spotifyApi = new SpotifyWebApi({
      clientId: client_id,
      clientSecret: client_secret,
    })

    spotifyApi.setAccessToken(storedAcessToken)
    spotifyApi.setRefreshToken(storedRefreshToken)

    try {
      const playlistId = req.params.id
      let allTracks = []
      let tracksFeatures = []
      new Map(Object.entries(playlists[playlistId])).forEach((playlistUser) => {
        allTracks.push.apply(allTracks, playlistUser.top_tracks)
        tracksFeatures.push.apply(tracksFeatures, playlistUser.tracks_features)
      })
      res.send({
        status: 'ok'
      })
    } catch (err) {
      res.send({
        status: 'error',
        error: err,
      })
    }
  }
})

async function getTopTracks(spotifyApi) {

  const topTracksOptions = {
    limit: 50,
    time_range: 'medium_term',
    offset: 0
  }

  const topTracks = (await spotifyApi.getMyTopTracks(topTracksOptions)).body.items;
  let tracksIds = []
  topTracks.forEach((track) => {
    tracksIds.push(track.id)
  })

  const tracksFeatures = (await spotifyApi.getAudioFeaturesForTracks(tracksIds)).body.audio_features

  return [topTracks, tracksFeatures]
}

/**
 * Export app
 */
module.exports = app

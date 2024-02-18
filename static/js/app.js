var janus = null;
var sipcall = null;
var opaqueId = "siptest-" + Janus.randomString(12);
var selectedApproach = "guest";
var registered = false;
var localTracks = {},
    remoteTracks = {};
const initJanus = () => {
    Janus.init({
        debug: "all",
        callback: function() {
            if (!Janus.isWebrtcSupported()) {
                bootbox.alert("No WebRTC support... ");
                return;
            }
            janus = new Janus({
                server: "https://" + janus_domain + "/janus",
                iceServers: iceServers,
                success: function() {
                    janus.attach({
                        plugin: "janus.plugin.sip",
                        opaqueId: opaqueId,
                        success: function(pluginHandle) {
                            sipcall = pluginHandle;
                            Janus.log("Plugin attached! (" + sipcall.getPlugin() + ", id=" + sipcall.getId() + ")");
                            registerPhone()
                        },
                        iceState: function(state) {
                            Janus.log("ICE state changed to " + state);
                        },
                        mediaState: function(medium, on, mid) {
                            Janus.log("Janus " + (on ? "started" : "stopped") + " receiving our " + medium + " (mid=" + mid + ")");
                        },
                        webrtcState: function(on) {
                            Janus.log("Janus says our WebRTC PeerConnection is " + (on ? "up" : "down") + " now");
                        },
                        slowLink: function(uplink, lost, mid) {
                            Janus.warn("Janus reports problems " + (uplink ? "sending" : "receiving") +
                                " packets on mid " + mid + " (" + lost + " lost packets)");
                        },
                        onmessage: function(msg, jsep) {
                            Janus.debug(" ::: Got a message :::", msg);
                            var error = msg["error"];
                            if (error) {
                                if (registered) {
                                    sipcall.hangup();
                                }
                                alert(error);
                                return;
                            }
                            var callId = msg["call_id"];
                            var result = msg["result"];
                            if (result && result["event"]) {
                                var event = result["event"];
                                console.log("Janus Logs", event);
                                if (event === 'registration_failed') {
                                    Janus.warn("Registration failed: " + result["code"] + " " + result["reason"]);
                                    $('.status').html('Registration failed')
                                    alert(result["code"] + " " + result["reason"]);
                                    return;
                                }
                                if (event === 'registered') {
                                    Janus.log("Successfully registered as " + result["username"] + "!");
                                    $('.status').html('Registered!');
                                    if (!registered) {
                                        registered = true;
                                        masterId = result["master_id"];
                                    }
                                    $('#_config').show();
                                } else if (event === 'calling') {
                                    Janus.log("Waiting for the peer to answer...");
                                    $('.status').html('Calling...');
                                    $('#_config').hide();
                                    $('#_phone').show();
                                } else if (event === 'accepting') {
                                    $('.status').html('Accepting the call!');
                                    console.log("Response to an offerless INVITE, let's wait for an 'accepted'")
                                } else if (event === 'progress') {
                                    $('.status').html('In Progress..!');
                                    Janus.log("There's early media from " + result["username"] + ", wairing for the call!", jsep);
                                    // Call can start already: handle the remote answer
                                    if (jsep) {
                                        sipcall.handleRemoteJsep({ jsep: jsep, error: doHangup });
                                    }
                                    console.info("[toaster.info] : Early media...");
                                } else if (event === 'accepted') {
                                    $('.status').html('In Call with ' + result["username"] + '!');
                                    Janus.log(result["username"] + " accepted the call!", jsep);
                                    // Call can start, now: handle the remote answer
                                    if (jsep) {
                                        sipcall.handleRemoteJsep({ jsep: jsep, error: doHangup });
                                    }
                                    console.log("[toaster.success] : Call accepted!");
                                    sipcall.callId = callId;
                                } else if (event === 'hangup') {
                                    Janus.log("Call hung up (" + result["code"] + " " + result["reason"] + ")!");
                                    $('.status').html(result["code"] + " " + result["reason"]);
                                    sipcall.hangup();
                                    $('#_phone').hide();
                                    $('#_config').show();
                                }
                            }
                        },
                        onlocaltrack: function(track, on) {
                            Janus.debug("Local track " + (on ? "added" : "removed") + ":", track);
                            // We use the track ID as name of the element, but it may contain invalid characters
                            var trackId = track.id.replace(/[{}]/g, "");
                            if (!on) {
                                // Track removed, get rid of the stream and the rendering
                                var stream = localTracks[trackId];
                                if (stream) {
                                    try {
                                        var tracks = stream.getTracks();
                                        for (var i in tracks) {
                                            var mst = tracks[i];
                                            if (mst)
                                                mst.stop();
                                        }
                                    } catch (e) {}
                                }
                                delete localTracks[trackId];
                                return;
                            }
                            // If we're here, a new track was added
                            var stream = localTracks[trackId];
                            if (stream) {
                                // We've been here already
                                return;
                            }
                            if (sipcall.webrtcStuff.pc.iceConnectionState !== "completed" &&
                                sipcall.webrtcStuff.pc.iceConnectionState !== "connected") {
                                console.log("Connecting...");
                            }
                        },
                        onremotetrack: function(track, mid, on) {
                            Janus.debug("Remote track (mid=" + mid + ") " + (on ? "added" : "removed") + ":", track);
                            if (!on) {
                                // Track removed, get rid of the stream and the rendering
                                delete remoteTracks[mid];
                                return;
                            }
                            // If we're here, a new track was added
                            if (track.kind === "audio") {
                                // New audio track: create a stream out of it, and use a hidden <audio> element
                                stream = new MediaStream([track]);
                                remoteTracks[mid] = stream;
                                Janus.log("Created remote audio stream:", stream);
                                $("#videoright").append('<audio class="hidden" id="peervideom' + mid + '" autoplay playsinline/>');
                                Janus.attachMediaStream($('#peervideom' + mid).get(0), stream);
                            }
                        },
                        oncleanup: function() {
                            Janus.log(" ::: Got a cleanup notification :::");
                            $('#videoright').empty();
                            $('.status').html('');
                            if (sipcall) {
                                delete sipcall.callId;
                                delete sipcall.doAudio;
                            }
                            localTracks = {};
                            remoteTracks = {};
                        }
                    });
                },
                error: function(error) {
                    Janus.error(error);
                    alert(error);
                    window.location.reload();
                },
                destroyed: function() {
                    window.location.reload();
                }
            });
        }
    });
}

const registerPhone = () => {
    // We're registering as guests, no username/secret provided
    var register = {
        request: "register",
        type: "secret",
        force_tcp: true,
        secret: secret,
        authuser: authuser,
        proxy: 'sip:' + pbx_domain,
        username: 'sip:' + authuser + '@' + pbx_domain
    };

    console.log("register : ", register);
    sipcall.send({ message: register });
}

$('#dialExt').click(function() {
    const extNumber = $("#extNumber").val();
    if (extNumber == "" || extNumber == null || extNumber == undefined) {
        alert("Please enter extension number.");
        return;
    }
    $("#extNumber").val('');
    Janus.log("This is a SIP audio call to sip:" + extNumber + "@" + pbx_domain);
    actuallyDoCall(sipcall, "sip:" + extNumber + "@" + pbx_domain);
})

const doCall = (e) => {
    const _sipUri = e.dataset.url;
    Janus.log("This is a SIP audio call to " + _sipUri);
    actuallyDoCall(sipcall, _sipUri);
}

const actuallyDoCall = (handle, _sipUri) => {
    handle.doAudio = true;
    let tracks = [{ type: 'audio', capture: true, recv: true }];
    handle.createOffer({
        tracks: tracks,
        success: function(jsep) {
            Janus.debug("Got SDP!", jsep);
            var body = { request: "call", uri: _sipUri };
            body["autoaccept_reinvites"] = false;
            handle.send({ message: body, jsep: jsep });
        },
        error: function(error) {
            Janus.error("WebRTC error...", error);
            alert("WebRTC error... " + error.message);
        }
    });
}

const doHangup = () => {
    var hangup = { request: "hangup" };
    sipcall.send({ message: hangup });
    sipcall.hangup();
}

$('.send_dtmf').click(function() {
    // Send DTMF tone (inband)
    // sipcall.dtmf({dtmf: { tones: $(this).text()}});
    // Notice you can also send DTMF tones using SIP INFO
    console.log("Sending DTMF : ", $(this).text());
    sipcall.dtmf({ dtmf: { tones: $(this).text() } });

    // sipcall.send({message: {request: "dtmf_info", digit: $(this).text()}});
});


const isEmpty = (data) => {
    if (data == null || data == "" || data == undefined) {
        return true;
    } else {
        return false;
    }
}
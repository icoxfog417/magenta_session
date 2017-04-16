var MIDIInterface = (function () {
    function MIDIInterface(playerTurnSeconds, magentaTurnSeconds) {
        this.inputDevice = null;
        this.outputDevice = null;
        this.inSession = false;
        this.recorded = [];
        this.keyStream = new KeyStream();
        this.playerTurnSeconds = playerTurnSeconds;
        this.magentaTurnSeconds = magentaTurnSeconds;
        this.playerInstrument = 32;
        this.synth = new Tone.PolySynth(8).toMaster();
        this.startTime = null;
        this.magentaTurn = false;
    };
    MIDIInterface.prototype.listen = function (callback) {
        var self = this;
        navigator.requestMIDIAccess({sysex:false}).then(
            function(ma){
                self.onDeviceConnect(ma);
                callback();
            }, self.onDeviceError);
    };
    MIDIInterface.prototype.onDeviceConnect = function (midiAccess) {
        var inputIterator = midiAccess.inputs.values();
        for(var o = inputIterator.next(); !o.done; o = inputIterator.next()) {
            this.inputDevice = o.value;
            console.log(this.inputDevice);
            break; //only 1 device
        }

        var outputIterator = midiAccess.outputs.values();
        for(var o = outputIterator.next(); !o.done; o = outputIterator.next()) {
            this.outputDevice = o.value;
            break;
        }

        if(this.inputDevice != null){
            var self = this;
            this.inputDevice.onmidimessage = function(event){
                self.onMIDIEvent(self, event);
            };
        }
    };
    MIDIInterface.prototype.onDeviceError = function () {
        console.log("error occurred!")
    };
    MIDIInterface.prototype.timeReset = function () {
        this.keyStream.reset();
        this.startTime = new Date();
    };
    MIDIInterface.prototype.session = function (isOn) {
        if(!this.inSession && isOn){//begin new session
            this.recorded = [];
        };
        this.inSession = isOn;
        this.magentaTurn = false;
        this.timeReset();
    };
    MIDIInterface.prototype.onMIDIEvent = function (self, event) {
        if(!self.inSession){
            return 0;
        }
        self.keyStream.in(event);
        self.step();
    };
    MIDIInterface.prototype.generate = function () {        
        this.magentaTurn = true;
        this.startTime = new Date(); // start Magenta Turn
        var playerTrack = this.keyStream.toTrack(this.playerInstrument);
        var response = MidiConvert.create();
        var self = this;
        var totalSeconds = this.playerTurnSeconds + this.magentaTurnSeconds;
        self.recorded.push([false, playerTrack]);
        setTimeout(function(){
            self.magentaTurn = false;
            self.timeReset();
        }, self.magentaTurnSeconds * 1000);
        response.load("/predict?duration=" + totalSeconds, JSON.stringify(playerTrack.toArray()), "POST").then(function(f){
            f = f.slice(self.playerTurnSeconds);
            self.recorded.push([true, f]);
            self.playMIDI(f);
        }, function(){
            self.magentaTurn = false;            
        });
    }

    MIDIInterface.prototype.getElapse = function () {
        var now = new Date();
        var elapse = now - this.startTime;
        var elapseSeconds = elapse / 1000;
        return elapseSeconds;
    }

    MIDIInterface.prototype.step = function () {
        var elapseSeconds = this.getElapse();
        var underBound = Math.round(elapseSeconds * 1000) / 1000;
        if(underBound >= this.playerTurnSeconds){
            if(this.keyStream.notePlays.length > 0 && !this.magentaTurn){
                this.generate();
            }else if(!this.magentaTurn){
                this.timeReset();
            }
        }
        return elapseSeconds;
    };
    MIDIInterface.prototype.playMIDI = function (midi) {
        Tone.Transport.bpm.value = midi.header.bpm;
        var melody = midi.tracks[1].notes;
        if(melody.length > 0){
            var self = this;
            var midiPart = new Tone.Part(function(time, note) {
                self.synth.triggerAttackRelease(note.name, note.duration, time, note.velocity)
            }, melody).start()
            
            Tone.Transport.start()
        }else{
            console.log("no melody found");
        }
    };

    MIDIInterface.prototype.getRecordedMIDI = function(){
        var recorded = MidiConvert.create();
        var startTime = 0;
        for(var i = 0; i < this.recorded.length; i++){
            var isMagenta = this.recorded[i][0];
            var midi = this.recorded[i][1];
            var track = isMagenta ? midi.tracks[1] : midi.tracks[0];
            var instrumentId = track.instrumentNumber.toString();
            var rTrack = recorded.get(instrumentId);
            if(!rTrack){
                rTrack = recorded.track(instrumentId);
                if(track.instrumentNumber > 0){
                    rTrack = rTrack.patch(track.instrumentNumber);
                }
            }
            track.notes.forEach(function(n){
                rTrack.note(n.name, n.time + startTime, n.duration);
            });
            startTime += track.duration;
        }
        return recorded;
    }

    MIDIInterface.prototype.downloadMIDI = function(midi){
        var a = document.createElement("a");
        a.download = "output.midi";
        a.target = "_blank";
        var bytechars = midi.encode();
        var byteNumbers = new Array(bytechars.length);
        for (var i = 0; i < bytechars.length; i++) {
            byteNumbers[i] = bytechars.charCodeAt(i);
        }
        var byteArray = new Uint8Array(byteNumbers);
        var blob = new Blob([byteArray], {type: 'application/x-pkcs12'})
        a.href = URL.createObjectURL(blob);
        a.click();
    }
    return MIDIInterface;
}());
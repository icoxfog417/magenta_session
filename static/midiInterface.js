var MIDIInterface = (function () {
    function MIDIInterface(playerTurnSeconds, magentaTurnSeconds) {
        this.inputDevice = null;
        this.outputDevice = null;
        this.inSession = false;
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
    MIDIInterface.prototype.session = function (isOn) {
        this.inSession = isOn;
        this.keyStream.reset();
        this.startTime = new Date();
        this.magentaTurn = false;
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
        var playerTrack = this.keyStream.toTrack(this.playerInstrument);
        console.log(playerTrack);
        var response = MidiConvert.create();
        var self = this;
        response.load("/predict?duration=" + this.magentaTurnSeconds, JSON.stringify(playerTrack.toArray()), "POST").then(function(f){
            self.playMIDI(f);
            //self.downloadMIDI(f);
            setTimeout(function(){
                self.magentaTurn = false;
            }, self.magentaTurnSeconds * 1000);
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
        if(elapseSeconds > this.playerTurnSeconds && !this.magentaTurn){
            if(this.keyStream.notePlays.length == 0){
                this.startTime = new Date(); //wait till midi in
                this.keyStream.reset();
            }else{
                this.generate();
                this.startTime = new Date(); //update for next
            }
        }
        return elapseSeconds;
    };
    MIDIInterface.prototype.playMIDI = function (midi) {
        Tone.Transport.bpm.value = midi.header.bpm;
        var melody = [];
        for(var i = midi.tracks.length - 1; i > -1; i--){
            if(midi.tracks[i].notes.length > 0){
                melody = midi.tracks[i].notes;
                break;
            }
        }
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
// message bus 
/*
 * methode: GestComp.Bus.fireEvent(origine,'message',[bus:obj/string],[msgcomplementaire:string])
 * origine est l'objet d'envois (souvent "this"), on affiche sa propriété "id", sauf si o est un objet
 * si objet, il doit posséder :
 * 		soit {origine:String,message:string,scroll:boolean} (ou l'un des 3 seulement, voire aucun
 * 		soit en propriété un objet "bus" comme ci-dessus   
 * 		scrool=true ou absent : force le scrolling à 0 (pour voir l'lélément) 
 * 		scrool=false : pas de scrolling auto
 */
 
 Ext.define('GestComp.message.Bus',{
 	extend:'Ext.util.Observable', 	
 	initComponent: function() {
 		GestComp.message.Bus.superclass.initComponent.apply(this, arguments);
 		this.addEvents('message');
 		this.addEvents('erreur');
 	}
 });
 // UN SEUL BUS ICI
 GestComp.Message=new GestComp.message.Bus

 
 Ext.define('GestComp.message.MessagePanel',{
 	extend:'Ext.Panel',
 	alias:'widget.messagepanel',
 	autoScroll:true
 	,bodyStyle:'font-size:12px'
 	,initComponent:function() {
 		var config = { 
 		}; // eo config
 		Ext.apply(this, Ext.apply(this.initialConfig, config));
 		GestComp.message.MessagePanel.superclass.initComponent.apply(this, arguments);
 		//si plusieurs bus croisés : this.bus=new GestComp.message.Bus
 		this.bus=GestComp.Message
 	}
 	,onRender:function() {
 		GestComp.message.MessagePanel.superclass.onRender.apply(this, arguments);
 		this.bus.on('message', this.onMessage, this);
 		this.bus.on('erreur', this.onErreur, this);
 	}
 	,onMessage:function(origine,o,msgcomp) {this.DisplayMessage(origine,o,msgcomp,false)}
 	,onErreur:function(origine,o,msgcomp) {this.DisplayMessage(origine,o,msgcomp,true)}
 	,DisplayMessage:function(origine,o,msgcomp,error) {
 		d=new Date() ; 	
 		scroll=true;
 		if (Ext.isObject(o)) {
 			if (o.bus) {
 				message=Ext.Date.format(d,'G:i:s')+
 					':<b>'+(o.bus.origine?o.bus.origine:'')+'</b>: '+(o.bus.message?o.bus.message:'')+
 					(msgcomp?'('+msgcomp+')':'')
 				if (typeof o.bus.scroll != "undefined") scroll=o.bus.scroll; 			
 			} else {
 				message=Ext.Date.format(d,'G:i:s')+
 					':<b>'+(o.origine?o.origine:'')+'</b>: '+(o.message?o.message:'')+
 					(msgcomp?'('+msgcomp+')':'')
 				if (typeof o.scroll != "undefined") scroll=o.scroll
 			}
 		} else {
 			message=Ext.Date.format(d,'G:i:s')+': <b>'+o+'</b>: '+msgcomp+' (venant de '+origine.id+')'
 		}	
 		if (error) message='<span style="color:red">'+message+'</span>'
 		if (this.body.first() != null) this.body.first().setStyle('color','grey')
 		this.body.insertFirst({html:message}); 	
 		if (scroll) this.body.scrollTo('top',0,true)
 	} 
});

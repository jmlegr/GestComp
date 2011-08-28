/**
 * @class Ext.ux.tree.X3TreeGrid
 * This class handles quite a few things for our implementation of the ExTJS TreeGrid as well as fixing a few bugs:<ul>
 * <li>Create custom events columnWidthsUpdated and sortHasChanged which are pretty self-explanatory. You can use
 *   these to be set as the stateEvents if you want to save the state of the column widths and sort.</li>
 * <li>Apply a default sort if the initial column definition contains a column with a 'dir' property.</li>
 * <li>Fix a bug where any sort other than the default sort was not working in the 3.1.1 release of the ExtJS TreeGrid</li>
 * <li>Fix a bug where the horizontal scrollbar would disappear if you set a top toolbar</li>
 * <li>Fix a bug where the header would not sync. probably under IE when doing an horizontal scrollbar.</li>
 * <li>Implement a getState method that will automatically make a callback to the URL you specify if desired, POSTing 
 * a JSON string with the column width and sort order so that it can be saved server-side.</li></ul>
 * @author <a href="mailto:sylvain.bujold@emaint.com">Sylvain Bujold</a>
 * @extends Ext.ux.tree.TreeGrid
 * 
 * @xtype x3treegrid
 */
Ext.ux.tree.X3TreeGrid = Ext.extend(Ext.ux.tree.TreeGrid, {
    initComponent : function() {
        // add custom events that can be used in stateEvents if desired
        this.addEvents('columnWidthsUpdated','sortHasChanged');
        
        // This event must be registered before the parent class because the
        // handler in TreeGridSorter returns false causing the event propagation to stop
        // and therefore our onHeaderMenuClick handler would not fire
        this.on('headermenuclick', this.onHeaderMenuClick, this);
        
        // Tie into headerclick event to fire our custom events
        this.on('headerclick', this.onHeaderClick, this);
        
        // call parent init component
        Ext.ux.tree.X3TreeGrid.superclass.initComponent.call(this);
        
        // AfterRender event handler that will apply the default sort and fix a display bug
        this.on('afterrender', this.onAfterRender, this, {single: true});
        
        /**
         * The defaultSortFn in Ext.ux.tree.TreeGridSorter has a bug. It calls sortType passing the full node
         * instead of just the value. fix this in our subclass instead of modifying TreeGridsorter.js
         * @ignore
         */
        this.treeGridSorter.defaultSortFn = function(n1, n2){
            var dsc = me.dir && me.dir.toLowerCase() == 'desc';
            var p = me.property || 'text';
            var sortType = me.sortType;
            var fs = me.folderSort;
            var cs = me.caseSensitive === true;
            var leafAttr = me.leafAttr || 'leaf';
            if(fs){
                if(n1.attributes[leafAttr] && !n2.attributes[leafAttr]){
                return 1;
            }
            if(!n1.attributes[leafAttr] && n2.attributes[leafAttr]){
                return -1;
                }
            }
            
            var v1 = sortType ? sortType(n1.attributes[p]) : (cs ? n1.attributes[p] : n1.attributes[p].toUpperCase());
            var v2 = sortType ? sortType(n2.attributes[p]) : (cs ? n2.attributes[p] : n2.attributes[p].toUpperCase());
            if(v1 < v2){
                return dsc ? +1 : -1;
            }else if(v1 > v2){
                return dsc ? -1 : +1;
            }else{
                return 0;
            }
        };
    },

    /**
     * AfterRender event handler that will apply the default sort and fix a display bug
     * @private
     * @name Ext.ux.tree.X3TreeGrid#onAfterRender
     */
    onAfterRender : function() {
        //Appy the default sort. Right after render, the first column that we find a 'dir' property filled in with a 
        //sort direction we call the header click handler which will apply the sort. This implies that the default
        //sort you want must be 'reversed' since the click handler switches from asc to desc and vice-versa.
        for (var i = 0; i < this.columns.length; i++) {
            if (this.columns[i].dir && this.columns[i].dir.trim() !== '') {
                this.treeGridSorter.onHeaderClick(this.columns[i], null, i);
                break;
            }
        }
        
        //This will fix a bug when the TreeGrid Panel' has a toolbar defined, 
        //the Panel's body it the same size as the root node div and therefore it hides the scrollbar. Make room for it.
        if (this.tbar) {
            var tree = this.getTreeEl();
            if (tree) {
                tree.setHeight(tree.getHeight()+23);
            }
        }
    },
    
    /**
     * Handle a header menu click, if it's a change sort option that was click call the 'onHeaderClick' handler as if
     * the corresponding header had been clicked directly.
     * @name Ext.ux.tree.X3TreeGrid#onHeaderMenuClick
     */
    onHeaderMenuClick : function(c, id, index) {
        if(id === 'asc' || id === 'desc') {
            this.onHeaderClick(c, null, index);
        }
    },
    
    /**
     * Handle a header click. The TreeGridSorter class also listen to this same event and is the one responsible to do
     * the actual sort. This handler is mostly responisble to fire our custom event 'sortHaschanged'
     * @name Ext.ux.tree.X3TreeGrid#onHeaderClick
     */
    onHeaderClick : function(c, el, i) {
        if(c && !this.headersDisabled) {
            var me = {};
            me.property = c.dataIndex;
            me.dir = (c.dir === 'desc' ? 'asc' : 'desc');
            this.fireEvent('sortHasChanged',this,me);
        }
    },
    
    /**
     * Subclas of the Ext.ux.tree.TreeGrid updateColumnWidths method so that we can fire a custom
     * 'columnWidthsUpdated' event.
     * @name Ext.ux.tree.X3TreeGrid#updateColumnWidths
     */
    updateColumnWidths : function() {
        //Call parent class code
        Ext.ux.tree.X3TreeGrid.superclass.updateColumnWidths.call(this);
        //Fire custom event
        this.fireEvent('columnWidthsUpdated',this);
    },
    
    /**
     * Subclass of the Ext.ux.tree.TreeGrid syncHeaderScroll method so that we can fix a bug where the header
     * doesn't scroll horizontally correctly under IE 6 and 7.
     * @name Ext.ux.tree.X3TreeGrid#syncHeaderScroll
     * @private
     */
    syncHeaderScroll : function(){
        //Call parent class code
        Ext.ux.tree.X3TreeGrid.superclass.syncHeaderScroll.call(this);
        //Force the browser to redraw by 'modifying' the Dom...
        this.innerHd.removeClass('whatever');
    },
    
    /**
     * function called by the treegrid getState function. This normally should have been handled by
     * an implementation of the ExtJS State Manager that would use Ajax hits to save/get the state
     * in a userpref, but it was simple enough to just have a save method and handle the state upon load.
     * @name Ext.ux.tree.X3TreeGrid#saveTreeGridState
     * @private
     */
    saveTreeGridState : function saveTreeGridState(state) {
    
        var save = false;
        var stateJson = Ext.encode(state);
        
        //Verify if the state has changed since the last time we saved it
        if (this.treeGridSavedState) {
            if (this.treeGridSavedState !== stateJson) {
                save = true;
            }
        } else {
            save = true;
        }
        
        //The state has changed, save it on the server
        if (save  && this.stateSaveUrl) {
            Ext.Ajax.request({
                url: this.stateSaveUrl,
                method: "POST",
                callback: Ext.emptyFn,
                jsonData: stateJson
            });
            this.treeGridSavedState = stateJson;
        }
    },
    
    /**
     * Keeps a copy of the state in JSON as it was the alst time it was saved so that it can be compared against before making
     * a callback.
     * @name Ext.ux.tree.X3TreeGrid#treeGridSavedState
     * @private
     * @type object
     */
    treeGridSavedState : null,
    
    /**
     * Retrieve the 'state' which in this implementation consists of the column width and the sord order.
     * @name Ext.ux.tree.X3TreeGrid#getState
     */
    getState: function getState() {
        var state = {};
        state.columns = {};
        for (var i = 0; i < this.columns.length; i++) {
            state.columns[this.columns[i].dataIndex] = this.columns[i].width;
        }
        state.sort = {
            field: this.treeGridSorter.property,
            dir: this.treeGridSorter.dir
        };
        this.saveTreeGridState(state);
        return state;
    }
    
});

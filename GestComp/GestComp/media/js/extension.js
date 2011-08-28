/*
 * 
 */
 
// create namespace
Ext.ns('${namespace}');
 
/**
 * @class ${class}
 * @extends ${extends}
 *
 * AbstractPanel File Pattern
 *
 * @author    Jean-Marc Legrand
 * @copyright ${year} CC BY-SA-NC Jean-Marc Legrand
 * @version   0.1
 * @date      <ul>
 * <li>${date}</li>
 * </ul>
 * @revision  $$Id$$
 * @depends   
 *
 * @see       http://tdg-i.com/364/abstract-classes-with-ext-js
 * @see       http://blog.extjs.eu/know-how/writing-a-big-application-in-ext/
 * @see       http://blog.extjs.eu/know-how/factory-functions-in-ext-extensions/
 *
 * @license   This file is released under the
 * <a target="_blank" href="http://www.gnu.org/licenses/gpl.html">GNU GPL 3.0</a>
 * license. It’s free for use in GPL and GPL compatible open source software, 
 * but if you want to use the component in a commercial software (closed source),
 * you have to get a commercial license.
 */
${namespace}.${class} = Ext.extend(${extends}, {
 
    // default options - can be overridden on instantiation
    // Do NOT put arrays or objects here
     border:false
 
    // {{{
    // private
    ,initComponent:function() {
 
        // create config object
        var config = {};
 
        // build config
        this.buildConfig(config);
 
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
 
        // call parent
        ${namespace}.${class}.superclass.initComponent.call(this);
 
    } // eo function initComponent
    // }}}
    // {{{
    /**
     * Builds the config object
     * @param {Object} config The config object is passed here
     * from initComponent by reference. Do not create or return
     * a new config object, add to the passed one instead.
     *
     * You can override this function if you need to customize it
     * or you can override individual build functions called.
     */
    ,buildConfig:function(config) {
        this.buildItems(config);
        this.buildButtons(config);
        this.buildTbar(config);
        this.buildBbar(config);
    } // eo function buildConfig
    // }}}
    // {{{
    /**
     * Builds items
     * @param {Object} config The config object is passed here
     * from buildConfig by reference. Do not create or return
     * a new config object, add to the passed one instead.
     *
     * You can override this function if you need to customize it.
     */
    ,buildItems:function(config) {
        config.items = undefined;
    } // eo function buildItems
    // }}}
    // {{{
    /**
     * Builds buttons
     * @param {Object} config The config object is passed here
     * from buildConfig by reference. Do not create or return
     * a new config object, add to the passed one instead.
     *
     * You can override this function if you need to customize it.
     */
    ,buildButtons:function(config) {
        config.buttons = undefined;
    } // eo function buildButtons
    // }}}
    // {{{
    /**
     * Builds top toolbar and its items
     * @param {Object} config The config object is passed here
     * from buildConfig by reference. Do not create or return
     * a new config object, add to the passed one instead.
     *
     * You can override this function if you need to customize it.
     */
    ,buildTbar:function(config) {
        config.tbar = undefined;
    } // eo function buildTbar
    // }}}
    // {{{
    /**
     * Builds bottom toolbar and its items
     * @param {Object} config The config object is passed here
     * from buildConfig by reference. Do not create or return
     * a new config object, add to the passed one instead.
     *
     * You can override this function if you need to customize it.
     */
    ,buildBbar:function(config) {
        config.bbar = undefined;
    } // eo function buildBbar
    // }}}
 
}); // eo extend

// eof

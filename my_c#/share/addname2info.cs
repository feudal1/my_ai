using System;
using System.IO;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;

namespace tools
{
    public class add_name2info
    {
        static public void run(ModelDoc2 swModel)
        {
            try
            {
                string pathname = Path.GetFileNameWithoutExtension(swModel.GetPathName());
        
                var ConfigNames = (string[])swModel.GetConfigurationNames();
                Configuration? swConfig = null;
                
                foreach (var configName in ConfigNames)
                {
                             swConfig = (Configuration)swModel.GetConfigurationByName(configName);
                var manger = swModel.Extension.CustomPropertyManager[configName];
                object? vPropNames = null;
                object? vPropTypes = null;
                object? vPropValues = null;
                object[] propValues;
                object? resolved = null;
                object? linkProp = null;
                var nNbrProps = manger.Count;
                manger.GetAll3(ref vPropNames, ref vPropTypes, ref vPropValues, ref resolved, ref linkProp);
                propValues = (object[])vPropValues;
                var propNames = (string[])vPropNames;
                manger.Add3("名称", (int)swCustomInfoType_e.swCustomInfoText, pathname, (int)swCustomPropertyAddOption_e.swCustomPropertyReplaceValue);

                }
       

            }
            catch (Exception ex)
            {
                Console.WriteLine($"发生错误: {ex.Message}");
                Console.WriteLine("提示：请确保 SolidWorks 正在运行。");
            }
        }
    }
}
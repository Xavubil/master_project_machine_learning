using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Rest_Server_ML;

namespace Rest_Server_ML.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class MLController : ControllerBase
    {
        // GET: api/ML    --> train
        [HttpGet]
        public string Get()
        {
            MLClass.train();

            return "trained" ;
        }

        // GET: api/ML/5
        [HttpGet("{id}", Name = "Get")]
        public string Get(int id)
        {
           
            return "true";
        }

        // POST: api/ML    --> predict
        [HttpPost]
        public bool Post([FromBody] string values)
        {
            values.Replace(" ", "");
            string[] stringArray = values.Split(',');

            float[] floatArray = new float[stringArray.Length];


            for (int count = 0; count < stringArray.Length; count++)
            {
                floatArray[count] = float.Parse(stringArray[count], CultureInfo.InvariantCulture.NumberFormat);
            }

            DataFormat dataToPredict = new DataFormat();
            dataToPredict.featureVector = floatArray;

            return MLClass.predict(dataToPredict);
        }

        // PUT: api/ML/5
        [HttpPut("{id}")]
        public void Put(int id, [FromBody] string value)
        {
        }

        // DELETE: api/ApiWithActions/5
        [HttpDelete("{id}")]
        public void Delete(int id)
        {

        }
    }
}
